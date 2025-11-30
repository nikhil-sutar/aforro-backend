from django.db import transaction
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from apps.stores.models import Store, Inventory
from apps.orders.models import Order, OrderItem
from .serializers import OrderCreateSerializer, OrderDetailSerializer, StoreOrdersSerializer
from .pagination import OrdersPagination
from .tasks import send_order_confirmation_email
# Create your views here.

class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
        store = serializer.validated_data['store_id']
        items = serializer.validated_data['items']
        user = request.user

        with transaction.atomic():
            product_ids = [ item['product_id'].id for item in items]
            inventory_qs = Inventory.objects.select_for_update().select_related('product').filter(
                store = store,
                product__id__in = product_ids
            )

            inventory_map = {inventory.product.id: inventory for inventory in inventory_qs}
            print(inventory_map)
            total_order_amount = 0
            order_items = []
            can_fulfill = True

            for item in items:
                product_id = item['product_id'].id
                req_quantity = item['quantity_requested']
                
                if product_id not in inventory_map:
                    can_fulfill = False
                    break

                inventory_obj = inventory_map[product_id]
                if inventory_obj.quantity < req_quantity:
                    can_fulfill = False
                    break
                
                price = inventory_obj.product.price
                sub_total = price * req_quantity
                total_order_amount += sub_total

                order_items.append(OrderItem(
                    product = inventory_obj.product,
                    quantity_requested = req_quantity,
                    price_at_purchase = sub_total 
                ))

            status_val = Order.OrderStatus.CONFIRMED if can_fulfill else Order.OrderStatus.REJECTED
            final_amount = total_order_amount if can_fulfill else 0

            order = Order.objects.create(
                user = user,
                store = store,
                total_amount = final_amount,
                status = status_val
            ) 

            if can_fulfill:
                inventory_updates = []
                for item in order_items:
                    inventory_obj = inventory_map[item.product.id]
                    inventory_obj.quantity -= item.quantity_requested
                    inventory_updates.append(inventory_obj)
                    item.order = order

                Inventory.objects.bulk_update(inventory_updates, ['quantity'])
                OrderItem.objects.bulk_create(order_items)
                transaction.on_commit(
                    lambda: send_order_confirmation_email.delay(
                        email=user.email,
                        username=user.username,
                        order_id=order.id,
                        store_name=store.name,
                        total_amount=order.total_amount
                    )
                )
        
        response_serializer = OrderDetailSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class StoreOrdersListView(ListAPIView):
    serializer_class = StoreOrdersSerializer
    pagination_class = OrdersPagination
    
    def get_queryset(self):
        store_id = self.kwargs.get('store_id')
        orders = Order.objects.filter(store=store_id).annotate(total_items=Sum('items__quantity_requested')).order_by('-created_at')
        return orders