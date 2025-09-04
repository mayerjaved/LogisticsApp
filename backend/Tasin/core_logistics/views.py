# core_logistics/views.py

from rest_framework import status # <-- 1. ADD THIS IMPORT
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import DeliveryItem
from .serializers import DeliveryItemSerializer
from .mock_optimizer import run_mock_optimization

@api_view(['GET'])
def barcode_details(request, barcode):
    """
    Looks up a delivery item by its barcode and returns its details.
    """
    try:
        # 2. USE THE SERIALIZER TO GUARANTEE CORRECT DATA FORMAT
        item = DeliveryItem.objects.select_related('client', 'route').get(barcode=barcode)
        serializer = DeliveryItemSerializer(item)
        return Response(serializer.data)
    except DeliveryItem.DoesNotExist:
        # It's better practice to return a JSON error response
        return Response(
            {'error': 'Barcode not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

class OptimizeRouteView(APIView):
    """
    API endpoint that receives a list of barcodes, runs the mock optimization
    script, and returns the re-ordered list of delivery items.
    """
    def post(self, request, *args, **kwargs):
        barcodes = request.data.get('barcodes', [])

        if not isinstance(barcodes, list) or len(barcodes) < 2:
            return Response(
                {'error': 'A list of at least two barcodes is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        items_to_optimize = DeliveryItem.objects.select_related('client', 'route').filter(barcode__in=barcodes)

        if not items_to_optimize.exists():
             return Response(
                {'error': 'None of the provided barcodes were found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            run_mock_optimization(items_to_optimize)
            optimized_items = DeliveryItem.objects.filter(barcode__in=barcodes).order_by('delivery_index')
            serializer = DeliveryItemSerializer(optimized_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error during route optimization: {e}")
            return Response(
                {'error': 'An unexpected error occurred during optimization.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )