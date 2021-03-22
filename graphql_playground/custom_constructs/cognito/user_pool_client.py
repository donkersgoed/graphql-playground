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
    ) -> None:
        """Initialize the UserPoolClient Class."""
        super().__init__(scope, construct_id)

        if params['is_machine_client']:
            flows = cognito.OAuthFlows(
                client_credentials=True,
                authorization_code_grant=False,
                implicit_code_grant=False,
            )
            supported_identity_providers = []
            callback_urls = []
        else:
            flows = cognito.OAuthFlows(
                client_credentials=False,
                authorization_code_grant=True,
                implicit_code_grant=True,
            )
            supported_identity_providers = [
                cognito.UserPoolClientIdentityProvider.COGNITO
            ]
            callback_urls = [
                'https://jwt.io'
            ]

        self.user_pool_client = cognito.UserPoolClient(
            scope=self,
            id=f'playground-user-pool-client-{construct_id}',
            user_pool=params['user_pool'],
            supported_identity_providers=supported_identity_providers,
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

        # Set the callback_urls through the L1 construct
        # Get the L1 CDK construct
        cfn_user_pool_client = self.user_pool_client.node.children[0]
        # Add override for CallbackURLs
        cfn_user_pool_client.add_override('Properties.CallbackURLs', callback_urls)
