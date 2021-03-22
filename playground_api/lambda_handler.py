"""Lambda handler for deployment functions."""

# Standard library imports
from datetime import datetime

# Related third party imports
#-

# Local application/library specific imports
from controllers.inventory_controller import InventoryController

def handle_add_car(event, _context):
    """Add an car to DynamoDB."""

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

    # We only want the values that start with 'car/', but without the prefix.
    selection_set_list_car_keys = [
        car_key[len('car/'):] for car_key in selection_set_list if car_key.startswith('car/')
    ]

    # Instantiate a new InventoryController
    inventory_controller = InventoryController()

    try:
        # Add the car to the inventory
        added_car = inventory_controller.add_car(**event['arguments'])
        # `added_car` is a dictionary of car properties, e.g.:
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
            added_car_key: added_car_value
            for added_car_key, added_car_value in added_car.items()
            if added_car_key in selection_set_list_car_keys
        }
        return {
            'success': True,
            'car': return_dict
        }
    except Exception as exc:  # pylint: disable=broad-except
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
