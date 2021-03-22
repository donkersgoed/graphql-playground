
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

    def add_item(self, item_type: str, item: dict) -> dict:
        """Add an item (Car or Book) to DynamoDB."""
        item_uuid = str(uuid.uuid4())

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
