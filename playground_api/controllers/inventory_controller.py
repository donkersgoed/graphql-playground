
# Standard library imports
from datetime import datetime
import os
import uuid

# Related third party imports
import boto3

# Local application/library specific imports
#-

class InventoryController:
    """The InventoryController is reponsible for Inventory read and write operations."""

    def __init__(self):
        self.inventory_table = boto3.resource('dynamodb').Table(
            name=os.environ.get('INVENTORY_TABLE')
        )

    def add_car(self, car: dict) -> dict:
        """Add a car to DynamoDB."""
        item_uuid = str(uuid.uuid4())

        car_data = {
            'PK': 'ITEM',
            'SK': f'CAR#{item_uuid}',
            'id': item_uuid,
            'dateAdded': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
            **car
        }

        self.inventory_table.put_item(
            Item=car_data
        )
        return car_data
