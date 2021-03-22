"""Lambda handler for deployment functions."""

# Standard library imports
#-

# Related third party imports
#-

# Local application/library specific imports
from controllers.inventory_controller import InventoryController


def handle_add_book(event, _context):
    """Add a book to DynamoDB."""
    return _add_item('book', event)

def handle_add_car(event, _context):
    """Add a car to DynamoDB."""
    return _add_item('car', event)

def _add_item(item_type: str, event: dict) -> dict:
    """Add an Item (car or book) to DynamoDB."""
    print(event)
    # Retrieve the selection set provided by the client. This might look like this:
    # "selectionSetList": [
    #     "car",
    #     "car/id",
    #     "car/make",
    #     "car/model",
    #     "car/color",
    #     "car/continentOfOrigin",
    #     "car/countryOfOrigin"
    # ]
    # We only need to return the values the client is querying, so we use the selectionSetList
    # to drop any other value.
    selection_set_list = event['selectionSetList']

    # We only want the values that start with 'car/' or 'book/', but without the prefix.
    selection_set_list_item_keys = [
        item_key[len(f'{item_type}/'):] for item_key in selection_set_list if item_key.startswith(f'{item_type}/')
    ]

    # Instantiate a new InventoryController
    inventory_controller = InventoryController()

    try:
        # Add the item to the inventory. `event['arguments']` might look like this:
        # {
        #     "arguments": {
        #         "car": {
        #             "make": "Tesla",
        #             "model": "Model 3",
        #             "color": "white",
        #             "continentOfOrigin": "EUROPE"
        #         }
        #     }
        # }
        added_item = inventory_controller.add_item(
            item_type=item_type,
            item=event['arguments'][item_type]
        )
        print(added_item)
        # `added_item` is a dictionary of item properties, e.g.:
        # {
        #     "PK": "ITEM",
        #     "SK": "CAR#b59ae8c5-12a6-4774-a3fe-a4a53bae2331",
        #     "id": "b59ae8c5-12a6-4774-a3fe-a4a53bae2331",
        #     "dateAdded": "2021-03-22T10:51:41.386Z",
        #     "make": "Tesla",
        #     "model": "Model 3"
        # }

        # Build a response based on the selectionSetList
        return_dict = {
            added_item_key: added_item_value
            for added_item_key, added_item_value in added_item.items()
            if added_item_key in selection_set_list_item_keys
        }
        return {
            'success': True,
            item_type: return_dict
        }
    except Exception as exc:  # pylint: disable=broad-except
        print(exc)
        return {
            'success': False,
            'error_type': type(exc).__name__,
            'error': str(exc),
        }

def handle_get_inventory(event, _context):
    """Get items (cars, books or both) from DynamoDB."""

    return {
        'success': True,
        # **results,
    }
