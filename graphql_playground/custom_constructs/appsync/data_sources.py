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
        **kwargs
    ) -> None:
        """Initialize AppSyncDataSources Class."""
        super().__init__(scope, construct_id, **kwargs)

        file_path = os.path.dirname(os.path.realpath(__file__))
        request_templates_path = f'{file_path}/../../../graphql/request_mapping_templates'
        response_templates_path = f'{file_path}/../../../graphql/response_mapping_templates'

        # A NoneDataSource has no backing data. Processing is purely done in the templates.
        who_am_i_data_source = appsync.NoneDataSource(
            scope=self,
            id='lz_graphql_who_am_i_datasource',
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
            }
        )
        # Give this function access read access to the Items Table
        params['items_ddb_table'].grant_read_data(playground_get_inventory.function)

        playground_at_item = LambdaResolverDataSource(
            scope=self,
            construct_id='playground_at_item',
            params={
                'api': params['graphql_api'],
                'type_name': 'Mutation',
                'field_name': 'addItem',
                'lambda_handler': 'handle_at_item',
                'required_scopes': [
                    'scopes/items:write',
                ],
            }
        )
        # Give this function access write access to the Items Table
        params['items_ddb_table'].grant_write_data(playground_at_item.function)
