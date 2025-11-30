from django.urls import path
from .views import CreateOrderView, StoreOrdersListView


urlpatterns = [
    path('orders/',CreateOrderView.as_view(),name='create-order'),
    path('stores/<int:store_id>/orders/',StoreOrdersListView.as_view(),name='store-order-list'),
]