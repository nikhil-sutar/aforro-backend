from rest_framework import serializers
from apps.stores.models import Store
from apps.orders.models import Order, OrderItem
from apps.products.models import Product


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity_requested = serializers.IntegerField(min_value = 1)

class OrderCreateSerializer(serializers.Serializer):
    store_id = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())
    items = OrderItemInputSerializer(many=True, allow_empty=False)

class OrderItemDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.title', read_only=True)
    class Meta:
        model = OrderItem
        fields = [
            'id', 
            'product_name', 
            'quantity_requested', 
            'price_at_purchase' 
        ]

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemDetailSerializer(many=True, read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 
            'store_name', 
            'status', 
            'total_amount', 
            'created_at', 
            'items'
        ]

class StoreOrdersSerializer(serializers.ModelSerializer):
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = ['id','status','created_at','total_items']

