"""AppSync Data Sources module."""

# Standard library imports
import os

# Related third party imports
from aws_cdk import (
    aws_appsync as appsync,
    core,
)

# Local application/library specific imports
from custom_constructs.appsync.lambda_resolver_data_source import LambdaResolverDataSource


class AppSyncDataSources(core.Construct):
    """Construct for the AppSync data sources."""

    def __init__(  # pylint: disable=too-many-locals
        self,
        scope: core.Construct,
        construct_id: str,
        params: dict,
    ) -> None:
        """Initialize AppSyncDataSources Class."""
        super().__init__(scope, construct_id)

        file_path = os.path.dirname(os.path.realpath(__file__))
        request_templates_path = f'{file_path}/../../../graphql/request_mapping_templates'
        response_templates_path = f'{file_path}/../../../graphql/response_mapping_templates'

        # A NoneDataSource has no backing data. Processing is purely done in the templates.
        who_am_i_data_source = appsync.NoneDataSource(
            scope=self,
            id='playground_who_am_i_datasource',
            api=params['graphql_api']
        )

        # The resolver binds the data source to the whoami query in the GraphQL schema
        who_am_i_data_source.create_resolver(
            type_name='Query',
            field_name='whoami',
            request_mapping_template=appsync.MappingTemplate.from_file(
                file_name=f'{request_templates_path}/whoami.vtl'
            ),
            response_mapping_template=appsync.MappingTemplate.from_file(
                file_name=f'{response_templates_path}/whoami.vtl'
            ),
        )

        playground_get_inventory = LambdaResolverDataSource(
            scope=self,
            construct_id='playground_get_inventory',
            params={
                'api': params['graphql_api'],
                'type_name': 'Query',
                'field_name': 'getInventory',
                'lambda_handler': 'handle_get_inventory',
                'required_scopes': [
                    'scopes/items:read',
                ],
                'environment': {
                    'INVENTORY_TABLE': params['inventory_ddb_table'].table_name,
                },
            }
        )
        # Give this function access read access to the Items Table
        params['inventory_ddb_table'].grant_read_data(playground_get_inventory.function)

        playground_add_car = LambdaResolverDataSource(
            scope=self,
            construct_id='playground_add_car',
            params={
                'api': params['graphql_api'],
                'type_name': 'Mutation',
                'field_name': 'addCar',
                'lambda_handler': 'handle_add_car',
                'required_scopes': [
                    'scopes/items:write',
                ],
                'environment': {
                    'INVENTORY_TABLE': params['inventory_ddb_table'].table_name,
                },
            }
        )
        # Give this function access write access to the Items Table
        params['inventory_ddb_table'].grant_write_data(playground_add_car.function)

        playground_add_book = LambdaResolverDataSource(
            scope=self,
            construct_id='playground_add_book',
            params={
                'api': params['graphql_api'],
                'type_name': 'Mutation',
                'field_name': 'addBook',
                'lambda_handler': 'handle_add_book',
                'required_scopes': [
                    'scopes/items:write',
                ],
                'environment': {
                    'INVENTORY_TABLE': params['inventory_ddb_table'].table_name,
                },
            }
        )
        # Give this function access write access to the Items Table
        params['inventory_ddb_table'].grant_write_data(playground_add_book.function)

        playground_get_books = LambdaResolverDataSource(
            scope=self,
            construct_id='playground_get_books',
            params={
                'api': params['graphql_api'],
                'type_name': 'Query',
                'field_name': 'getBooks',
                'lambda_handler': 'handle_get_books',
                'required_scopes': [
                    'scopes/items:read',
                ],
                'environment': {
                    'INVENTORY_TABLE': params['inventory_ddb_table'].table_name,
                },
            }
        )
        # Give this function access write access to the Items Table
        params['inventory_ddb_table'].grant_read_data(playground_get_books.function)

        playground_get_cars = LambdaResolverDataSource(
            scope=self,
            construct_id='playground_get_cars',
            params={
                'api': params['graphql_api'],
                'type_name': 'Query',
                'field_name': 'getCars',
                'lambda_handler': 'handle_get_cars',
                'required_scopes': [
                    'scopes/items:read',
                ],
                'environment': {
                    'INVENTORY_TABLE': params['inventory_ddb_table'].table_name,
                },
            }
        )
        # Give this function access write access to the Items Table
        params['inventory_ddb_table'].grant_read_data(playground_get_cars.function)
