"""LambdaResolverDataSource module."""

import textwrap

from aws_cdk import (
    aws_appsync as appsync,
    aws_lambda as lambda_,
    aws_logs as logs,
    core,
)


class LambdaResolverDataSource(core.Construct):
    """Construct for a Lambda Resolver and Data Source."""

    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        """Initialize LambdaResolverDataSource Class."""
        super().__init__(scope, construct_id, **kwargs)

        # Take the provided parameters and add the `FUNCTION` parameter
        # which equals the provided Construct ID. This is purely used as a
        # logging parameter.
        env_vars = {
            **params['environment'],
            **{
                'FUNCTION': construct_id
            }
        }

        # Override the memory_size if provided
        memory_size = 512
        if 'memory_size' in params:
            memory_size = params['memory_size']
        # Override the timeout if provided
        timeout = core.Duration.seconds(60)
        if 'timeout' in params:
            timeout = params['timeout']

        # Create the Lambda Function
        self.function = lambda_.Function(
            scope=self,
            id=f'{construct_id}-function-v2',
            function_name=construct_id,
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.asset('backend_api'),
            layers=params['layers'],
            timeout=timeout,
            tracing=lambda_.Tracing.ACTIVE,
            handler=f"lambda_handler.{params['lambda_handler']}",
            environment=env_vars,
            memory_size=memory_size,
        )

        # Create a Data Source for this function
        data_source = appsync.LambdaDataSource(
            scope=self,
            id=f'{construct_id}_data_source'.replace('-', '_'),  # No dashes allowed
            lambda_function=self.function,
            api=params['api'],
        )

        # Create the request mapping template with the provided scopes
        required_scopes = "', '".join(params['required_scopes'])
        scope_check_template = textwrap.dedent(
            """\
                #set($requiredScopes = ['{required_scopes}'])
                #set($userScopes = $context.identity.claims.get("scope").split(" "))

                #foreach ($requiredScope in $requiredScopes)
                    #if(!$userScopes.contains($requiredScope))
                        $utils.error("Scope '$requiredScope' is required")
                    #end
                #end
                {
                    "version" : "2017-02-28",
                    "operation": "Invoke",
                    "payload": {
                        "arguments": $util.toJson($context.args),
                        "selectionSetList": $utils.toJson($context.info.selectionSetList)
                    }
                }
            """
        ).replace('{required_scopes}', required_scopes)

        # Bring it all together in a resolver. This will attach the Lambda Data Source
        # and Request Template to the given field in the GraphQL Schema.
        data_source.create_resolver(
            type_name=params['type_name'],
            field_name=params['field_name'],
            request_mapping_template=appsync.MappingTemplate.from_string(
                template=scope_check_template
            )
        )
