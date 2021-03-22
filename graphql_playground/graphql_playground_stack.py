"""The GraphqlPlaygroundStack module contains the main Stack."""

# Standard library imports
import os

# Related third party imports
from aws_cdk import (
    aws_appsync as appsync,
    aws_dynamodb as dynamodb,
    core,
)

# Local application/library specific imports
from custom_constructs.appsync.data_sources import AppSyncDataSources
from custom_constructs.cognito.user_pool import UserPool


class GraphqlPlaygroundStack(core.Stack):
    """The GraphqlPlaygroundStack class contains all CFN resources for the playground."""
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the UserPool components (including Resource Server and User Pool Clients)
        cognito = UserPool(
            scope=self,
            construct_id='cognito-construct'
        )

        # The DynamoDB table to store the cars and other objects
        inventory_table = dynamodb.Table(
            scope=self,
            id='inventory-table',
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            partition_key=dynamodb.Attribute(
                name='PK',
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name='SK',
                type=dynamodb.AttributeType.STRING
            ),
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
                        user_pool=cognito.user_pool
                    )
                )
            ),
            schema=appsync.Schema.from_asset(
                file_path=schema_file_path
            )
        )

        AppSyncDataSources(
            scope=self,
            construct_id='appsync-datasources',
            params={
                'graphql_api': graphql_api,
                'inventory_ddb_table': inventory_table,
            }
        )
