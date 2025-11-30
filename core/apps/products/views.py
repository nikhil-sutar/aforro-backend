from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework import filters

from .serializers import ProductSearchSerializer
from .models import Product
from .filters import ProductFilter
from .pagination import ProductPagination

# Create your views here.
class ProductSearchView(ListAPIView):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSearchSerializer
    pagination_class = ProductPagination

    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = ProductFilter
    search_fields = ['title','description','category__name']
    ordering_fields = ['price','created_at']
    ordering = ['-created_at']

    def get_ordering(self):
        ordering = self.request.query_params.get('ordering', '')
        if ordering == 'relevance':
            search_query = self.request.query_params.get('search', '')
            if search_query:
                return None
            else:
                return ['-created_at']
        return super().get_ordering()