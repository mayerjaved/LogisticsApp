from rest_framework import serializers
from .models import DeliveryItem

class DeliveryItemSerializer(serializers.ModelSerializer):
    """
    Serializes DeliveryItem data for the frontend, including related fields.
    """
    # Pull the client's name from the related Client model
    client_name = serializers.CharField(source='client.name', read_only=True)
    # Pull the client's address from the related Client model
    delivery_address = serializers.CharField(source='client.address', read_only=True)
    # Get the ID of the route for frontend logic
    route_id = serializers.IntegerField(source='route.id', read_only=True, allow_null=True)

    class Meta:
        model = DeliveryItem
        # Define the fields to include in the JSON output
        fields = [
            'id',
            'item_name',
            'barcode',
            'delivery_address',
            'due_time',
            'client_name',
            'route_id',
            'delivery_index', # This field is crucial for the new order
        ]