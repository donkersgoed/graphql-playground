"""UserPoolAndClients module."""

from aws_cdk import (
    aws_cognito as cognito,
    core,
)


class UserPoolAndClients(core.Construct):
    """Construct for a Lambda Resolver and Data Source."""

    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        """Initialize LambdaResolverDataSource Class."""
        super().__init__(scope, construct_id, **kwargs)

        # Create Cognito User pool
        self.user_pool = cognito.UserPool(
            scope=self,
            id='playground-user-pool',
        )
