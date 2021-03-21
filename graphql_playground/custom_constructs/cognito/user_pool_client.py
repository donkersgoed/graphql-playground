"""UserPoolClient module."""

# Standard library imports
# -

# Related third party imports
from aws_cdk import (
    aws_cognito as cognito,
    core,
)

# Local application/library specific imports
# -


class UserPoolClient(core.Construct):
    """Construct for a User Pool Client."""

    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        params,
        **kwargs,
    ) -> None:
        """Initialize the UserPoolClient Class."""
        super().__init__(scope, construct_id, **kwargs)

        if params['is_machine_client']:
            flows = cognito.OAuthFlows(
                client_credentials=True,
                authorization_code_grant=False,
                implicit_code_grant=False,
            )
        else:
            flows = cognito.OAuthFlows(
                client_credentials=False,
                authorization_code_grant=True,
                implicit_code_grant=True,
            )

        self.user_pool_client = cognito.UserPoolClient(
            scope=self,
            id=f'playground-user-pool-client-{construct_id}',
            user_pool=params['user_pool'],
            supported_identity_providers=[],
            o_auth=cognito.OAuthSettings(
                flows=flows,
                scopes=[
                    cognito.OAuthScope.resource_server(
                        params['resource_server'],
                        scope
                    ) for scope in params['scopes']
                ]
            ),
            generate_secret=params['is_machine_client'],
        )
