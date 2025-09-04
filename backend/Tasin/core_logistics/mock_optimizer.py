import random
from .models import DeliveryItem

def run_mock_optimization(delivery_items_queryset):
    """
    Takes a Django QuerySet of DeliveryItem objects, assigns a random 
    delivery_index to each, and saves the changes to the database.

    This function simulates a route optimization process.
    """
    # Convert queryset to a list to work with it
    items_list = list(delivery_items_queryset)
    
    if not items_list:
        return

    # Create a list of indices (e.g., [0, 1, 2] for 3 items)
    indices = list(range(len(items_list)))
    
    # Shuffle the indices to create a random order
    random.shuffle(indices)
    
    # Assign the new, shuffled index to each item
    for i, item in enumerate(items_list):
        item.delivery_index = indices[i]
        
    # Use bulk_update for efficiency. This saves all changes in a single
    # database query instead of one query per item.
    DeliveryItem.objects.bulk_update(items_list, ['delivery_index'])