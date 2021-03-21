"""Lambda handler for deployment functions."""

# Standard library imports
from datetime import datetime

# Related third party imports
#-

# Local application/library specific imports
#-

def handle_add_item(event, _context):
    """Add an item to DynamoDB."""

    return {
        'item': {
            'id': '1235',
            'name': 'Apple',
            'dateAdded': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
            'category': 'Fruit',
            'countryOfOrigin': 'Netherlands',
            'color': 'Red',
        }
    }

def handle_get_inventory(event, _context):
    """Get items from DynamoDB."""

    return {
        'success': True,
        # **results,
    }
