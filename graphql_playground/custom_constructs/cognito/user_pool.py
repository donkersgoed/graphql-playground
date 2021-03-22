"""UserPool module."""

# Standard library imports
import os

# Related third party imports
from aws_cdk import (
    aws_iam as iam,
    aws_cognito as cognito,
    custom_resources as cr,
    core,
)

# Local application/library specific imports
from custom_constructs.cognito.user_pool_client import UserPoolClient


class UserPool(core.Construct):
    """Construct for a Cognito User Pool and its User Pool Clients."""

    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        """Initialize the UserPool Class."""
        super().__init__(scope, construct_id, **kwargs)

        # Create a Cognito User Pool
        self.user_pool = cognito.UserPool(
            scope=self,
            id='playground-user-pool',
        )

        # Create a Cognito Admin User
        cognito.CfnUserPoolUser(
            scope=self,
            id='admin-user',
            user_pool_id=self.user_pool.user_pool_id,
            username='admin'
        )

        # Create a policy allowing us to set a permanent password.
        # Don't use this in production! It's only for demo purposes.
        allow_set_password = iam.PolicyStatement(
            actions=[
                'cognito-idp:AdminSetUserPassword',
            ],
            effect=iam.Effect.ALLOW,
            resources=[
                '*'
            ]
        )

        # Create Custom Resource to set the user password
        # Don't use this in production! It's only for demo purposes.
        cr.AwsCustomResource(
            scope=self,
            id='cognito-set-password-cr',
            on_create={
                'service': 'CognitoIdentityServiceProvider',
                'action': 'adminSetUserPassword',
                'parameters': {
                    'Password': 'thisisReally!1ns3cur3',
                    'Permanent': True,
                    'Username': 'admin',
                    'UserPoolId': self.user_pool.user_pool_id,
                },
                'physical_resource_id': cr.PhysicalResourceId.of(
                    id='CustomResourceAdminSetUserPassword'
                )
            },
            policy=cr.AwsCustomResourcePolicy.from_statements(
                statements=[allow_set_password]
            )
        )

        # Create UserPoolDomain
        cognito.UserPoolDomain(
            scope=self,
            id='playground-user-pool-domain',
            user_pool=self.user_pool,
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=os.environ.get('USER_POOL_DOMAIN_PREFIX')
            )
        )

        # Create ResourceServerScope for 'items:read'
        items_read_scope = cognito.ResourceServerScope(
            scope_name='items:read',
            scope_description='Allow read access item operations'
        )

        # Create ResourceServerScope for 'items:write'
        items_write_scope = cognito.ResourceServerScope(
            scope_name='items:write',
            scope_description='Allow write access item operations'
        )

        # Create ResourceServer for the User Pool, with the scopes
        # defined above.
        resource_server = cognito.UserPoolResourceServer(
            scope=self,
            id='playground-resource-server',
            user_pool=self.user_pool,
            identifier='scopes',
            scopes=[
                items_read_scope,
                items_write_scope,
            ]
        )

        # Create a Machine-to-Machine Client that's only allowed to read items
        UserPoolClient(
            scope=self,
            construct_id='user-pool-m2m-client-read',
            params={
                'user_pool': self.user_pool,
                'is_machine_client': True,
                'resource_server': resource_server,
                'scopes': [
                    items_read_scope,
                ]
            }
        )

        # Create a Machine-to-Machine Client that's only allowed to write items
        UserPoolClient(
            scope=self,
            construct_id='user-pool-m2m-client-write',
            params={
                'user_pool': self.user_pool,
                'is_machine_client': True,
                'resource_server': resource_server,
                'scopes': [
                    items_write_scope,
                ]
            }
        )

        # Create a Real User Client that's allowed to read and write items
        UserPoolClient(
            scope=self,
            construct_id='user-pool-client-humans',
            params={
                'user_pool': self.user_pool,
                'is_machine_client': False,
                'resource_server': resource_server,
                'scopes': [
                    items_read_scope,
                    items_write_scope,
                ]
            }
        )
