import django_filters
from django.db.models import Prefetch
from .models import Product
from apps.stores.models import Inventory

class ProductFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name='price',lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price',lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__name',lookup_expr='icontains')

    store_id = django_filters.NumberFilter(method='filter_store_inventory')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['price_min','price_max','category','store_id','in_stock']
    
    def filter_store_inventory(self, queryset, name, value):
        if value:
            store_inventory = Inventory.objects.filter(store=value)
            return queryset.prefetch_related(
                Prefetch('inventory', queryset=store_inventory, to_attr='my_stock')
            )
        return queryset
    
    def filter_in_stock(self, queryset, name, value):
        store_id = self.data.get('store_id') 
        if value and store_id:
            return queryset.filter(
                inventory__store_id=store_id, 
                inventory__quantity__gt=0
            )
        else:
            queryset = queryset.filter(
                inventory__quantity__gt=0
                )
        return queryset