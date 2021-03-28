"""The InventoryController module contains the InventoryController class."""
# Standard library imports
import base64
import os
import uuid
from datetime import datetime

# Related third party imports
import boto3
from boto3.dynamodb.conditions import Key, Attr

# Local application/library specific imports
# -


class InventoryController:
    """The InventoryController is reponsible for Inventory read and write operations."""

    def __init__(self) -> None:
        self.inventory_table = boto3.resource('dynamodb').Table(
            name=os.environ.get('INVENTORY_TABLE')
        )

    def add_item(self, item_type: str, item: dict) -> dict:
        """Add an item (Car or Book) to DynamoDB."""
        item_uuid = str(uuid.uuid4())

        # Add a few common values (PK, SK, id, date), then store all the attributes
        # provided by the client as-is.
        item_data = {
            'PK': 'ITEM',
            'SK': f'{item_type.upper()}#{item_uuid}',  # e.g. CAR#1234 or BOOK#5411
            'id': item_uuid,
            'dateAdded': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
            **item
        }

        self.inventory_table.put_item(
            Item=item_data
        )
        return item_data

    def get_items(self, params: dict) -> dict:
        """Get items from the inventory"""

        item_type = params['item_type']
        filter_parameters = params.get('filter')  # Optional, might return None
        limit = params.get('limit')  # Optional, might return None
        next_token = params.get('nextToken')  # Optional, might return None

        # Set up the basic parameters for the DynamoDB Query. The primary key
        # always contains the partition key 'ITEM' and the sort key starts
        # with CAR or BOOK, depending on what we're retrieving.
        query_params = {
            'KeyConditionExpression':
                Key('PK').eq('ITEM') &
                Key('SK').begins_with(f'{item_type.upper()}#')
        }

        # If get_items() is called with a list of attributes to return, build a ProjectionExpression.
        # This reduces the amount of data retrieved from DynamoDB to what we're actually requesting.
        if 'selection_set' in params:
            # `selection_set` looks like this:
            # [
            #     "resultCount",
            #     "nextToken",
            #     "items",
            #     "items/id",
            #     "items/make",
            #     "items/model",
            #     "items/color",
            #     "items/continentOfOrigin",
            #     "items/countryOfOrigin"
            # ]

            # We only want the selection set items with the prefix 'items/', and we want the prefix stripped.
            selection_set = [
                set_item[len('items/'):] for set_item in params['selection_set'] if set_item.startswith('items/')
            ]

            # Build a ProjectionExpression and ExpressionAttributeNames with the provided selection set,
            # then store them in the parameters provided to the DynamoDB Query.
            projection_expression = self._build_projection_expression(selection_set)
            query_params['ProjectionExpression'] = projection_expression['projection_expression']
            query_params['ExpressionAttributeNames'] = projection_expression['expression_attribute_names']

        # If the user provides filter parameters, build a FilterExpression with them
        # and provide it to the query. This filter will be applied after the query has retrieved
        # its results from DynamoDB.
        filter_expression = self._build_query_filter_expression(filter_parameters)
        if filter_expression:
            query_params['FilterExpression'] = filter_expression

        # If the user provides a limit, pass that limit on to the DynamoDB Query
        if limit:
            query_params['Limit'] = limit

        # If the user provides a next_token, decode it and pass it to the DynamoDB Query
        if next_token:
            decoded_next_token = base64.b64decode(next_token.encode()).decode()
            query_params['ExclusiveStartKey'] = {
                'PK': 'ITEM',
                'SK': f'{item_type.upper()}#{decoded_next_token}'
            }

        # Execute the query and retrieve the items
        ddb_response = self.inventory_table.query(**query_params)
        items = ddb_response['Items']

        last_evaluated_key_b64 = None
        last_evaluated_key = ddb_response.get('LastEvaluatedKey')
        if last_evaluated_key:
            # Grab the Sort Key and base64 encode it. This can be used by the client as
            # a `nextToken`, which will tell DynamoDB where to continue its next Query.
            last_evaluated_key_b64 = base64.b64encode(last_evaluated_key['SK'].encode()).decode()
        return {
            'items': items,
            'resultCount': len(items),
            'nextToken': last_evaluated_key_b64
        }

    @staticmethod
    def _build_projection_expression(selection_set: list) -> dict:
        """Build a ProjectionExpression and ExpressionAttributeNames for the provided set of GraphQL fields."""
        # The ProjectionExpression can't contain words like 'Region', so we use numbered references.
        # After building, the ProjectionExpression looks like this: "#K0, #K1"
        projection_expression = ', '.join(
            f'#K{index}' for index in range(len(selection_set))
        )

        # Then we create a map to link the #Kx values to the actual keys we want to resolve.
        # The final ExpressionAttributeNames look like this: {"#K0": "make", "#K1": "model"}
        expression_attribute_names = {
            f'#K{index}': selection_key for index, selection_key in enumerate(selection_set)
        }

        return {
            'projection_expression': projection_expression,
            'expression_attribute_names': expression_attribute_names
        }

    @staticmethod
    def _append_filter(source_filter, operation, additional_filter):
        if source_filter is None:
            # This is the first addition to the filter, return
            # the filter being added as-is.
            return additional_filter
        if additional_filter is None:
            # We're trying to add nothing to the source filter
            # so just return the source filter.
            return source_filter
        if operation == 'AND':
            return source_filter & additional_filter
        if operation == 'OR':
            return source_filter | additional_filter
        raise RuntimeError(f'Invalid operation: {operation}')

    def _build_query_filter_expression(self, filter_dict):  # pylint: disable=too-many-branches,too-many-statements
        """
        Build a complex Query Filter Expression to limit the results returned by DynamoDB.

        The filter_dict can have multiple keys, like make, model and color. Each
        of these keys can be filtered simultaneously, e.g. "all cars with make 'Tesla' and model 'Model 3'.

        The filters allow for five different operations: containsOr, containsAnd, notContains,
        equalsOr and notEquals.

        This function returns a single filter_expression, which consists of multiple key_filters (make,
        model, and so on), each of which has zero, one or more operations (containsOr, notEquals, and
        so on) which are defined in sub_key_filters.

        Example:
        filter_expression = (
            (key_filter_1) AND (key_filter_2) AND ... AND (key_filter_n)
        )

        Where key_filters look like:
        key_filter_x = (
            (sub_key_filter_1) AND/OR (sub_key_filter_2) AND/OR ... AND/OR (sub_key_filter_n)
        )

        Whether an AND or OR is applied depends on the filter, e.g. containsOr or containsAnd.
        """
        if not filter_dict:
            return None

        # We start with an empty filter expression
        filter_expression = None
        # Then we loop over every element of the filter_dict, defined just above.
        # This will return values like 'model', 'make', 'title' or other terms to filter on.
        for filter_key, filter_values in filter_dict.items():
            key_filter = None
            for filter_op, filter_op_values in filter_values.items():
                # e.g. filter_key = 'make', filter_op = 'containsOr', filter_op_values = ['esla', 'olksw']
                # This would filter the 'make' by items that contain 'esla' OR 'olkswag'.

                # Create a new sub filter for the multiple values for one key, for example
                # (make.contains('esla' OR 'olkswag')).
                sub_filter = None
                for filter_op_value in filter_op_values:
                    if filter_op == 'containsOr':
                        # Create a 'contains' comparison for every key, e.g. (make.contains('esla'))
                        sub_key_filter = Attr(filter_key).contains(filter_op_value)

                        # Then bind every sub_key_filter together with the OR operator. This creates a filter
                        # like (make.contains('esla' OR 'olkswag'))
                        sub_filter = self._append_filter(sub_filter, 'OR', sub_key_filter)

                    elif filter_op == 'containsAnd':
                        # Like the one above, but with an AND operator, for example (make.contains('Tes' AND 'la'))
                        # to match Tesla and Testorilla.
                        # Create a 'contains' comparison for every key, e.g. (make.contains('Tes'))
                        sub_key_filter = Attr(filter_key).contains(filter_op_value)

                        # Then bind every sub_key_filter together with the AND operator. This creates a filter
                        # like (make.contains('Tes' AND 'la'))
                        sub_filter = self._append_filter(sub_filter, 'AND', sub_key_filter)

                    elif filter_op == 'notContains':
                        # Like the one above, but with an Negate (~) operator, for example
                        # (make.notContains('Tes' AND 'Volksw')).
                        # Create a 'contains' comparison for every key, e.g. (make.contains('Tes'))
                        sub_key_filter = ~Attr(filter_key).contains(filter_op_value)

                        # Then bind every sub_key_filter together with the AND operator. This creates a filter
                        # like (make.notContains('Tes' AND 'Volksw'))
                        sub_filter = self._append_filter(sub_filter, 'AND', sub_key_filter)

                    elif filter_op == 'equalsOr':
                        # Create a 'equals' comparison for every key, e.g. (make.equals('Tesla'))
                        sub_key_filter = Attr(filter_key).eq(filter_op_value)

                        # Then bind every sub_key_filter together with the OR operator. This creates a filter
                        # like (make.equals('Tesla' OR 'Volkswagen'))
                        sub_filter = self._append_filter(sub_filter, 'OR', sub_key_filter)

                    elif filter_op == 'notEquals':
                        # Like the notContains one above, but with an equals operator, for example
                        # (make.notEquals('Tesla' AND 'Volkswagen')).
                        # Create a 'equals' comparison for every key, e.g. (make.notEquals('Tesla'))
                        sub_key_filter = ~Attr(filter_key).eq(filter_op_value)

                        # Then bind every sub_key_filter together with the AND operator. This creates a filter
                        # like (make.notEquals('Tesla' AND 'Volkswagen'))
                        sub_filter = self._append_filter(sub_filter, 'AND', sub_key_filter)

                # When all keywords have been combined, add it to key_filter with an AND operator.
                # This creates a filter like
                # "(make.notEquals('Tesla' AND 'Volkswagen')) AND (model.notEquals('Mach-E'))".
                key_filter = self._append_filter(key_filter, 'AND', sub_filter)

            # Finally, bind the key_filters together into filter_expression.
            filter_expression = self._append_filter(filter_expression, 'AND', key_filter)

        # Return the filter expression built after looping over the keys.
        return filter_expression
