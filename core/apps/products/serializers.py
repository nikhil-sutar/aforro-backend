from rest_framework import serializers

from .models import Product

class ProductSearchSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    inventory_quantity = serializers.SerializerMethodField(required=False, read_only=True)

    def get_inventory_quantity(self,obj):
        if hasattr(obj,'my_stock'):
            if obj.my_stock:
                return obj.my_stock[0].quantity
        return None

    class Meta:
        model = Product
        fields = ['id','title','description','price','category_name','inventory_quantity','created_at']
