
# Standard library imports
import os

# Related third party imports
from aws_cdk import (
    aws_appsync as appsync,
    core,
)
from dotenv import load_dotenv

# Local application/library specific imports
from custom_constructs.cognito.user_pool_and_clients import UserPoolAndClients
from custom_constructs.appsync.lambda_resolver_data_source import LambdaResolverDataSource


class GraphqlPlaygroundStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a Cognito User Pool and its User Pool Clients
        user_pool_and_clients = UserPoolAndClients(
            scope=self,
            construct_id='cognito'
        )

        # Define where the GraphQL schema is stored
        file_path = os.path.dirname(os.path.realpath(__file__))
        schema_file_path = f'{file_path}/../graphql/schema.graphql'

        # Create the GraphQL API
        graphql_api = appsync.GraphqlApi(
            scope=self,
            id='playground-graphql-api',
            name='playground-api',
            # Configure the GraphQL API to use Cognito User Pools for Authz
            authorization_config=appsync.AuthorizationConfig(
                default_authorization=appsync.AuthorizationMode(
                    authorization_type=appsync.AuthorizationType.USER_POOL,
                    user_pool_config=appsync.UserPoolConfig(
                        user_pool=user_pool_and_clients.user_pool
                    )
                )
            ),
            schema=appsync.Schema.from_asset(
                file_path=schema_file_path
            )
        )