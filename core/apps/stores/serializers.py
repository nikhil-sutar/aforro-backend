from rest_framework import serializers
from .models import Inventory

class InventorySerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    price = serializers.CharField(source='product.price', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)
    
    class Meta:
        model = Inventory
        fields = ['id', 'product_title', 'price', 'category_name', 'quantity']