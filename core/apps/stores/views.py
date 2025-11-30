from rest_framework.generics import ListAPIView

from .serializers import InventorySerializer
from .models import Inventory
from .pagination import InventoryProductPagination
# Create your views here.

class StoreInventoryListView(ListAPIView):
    serializer_class = InventorySerializer
    pagination_class = InventoryProductPagination
    def get_queryset(self):
        store_id = self.kwargs.get('store_id')
        inventory = Inventory.objects.filter(store=store_id).select_related('product','product__category').order_by('product__title')
        return inventory