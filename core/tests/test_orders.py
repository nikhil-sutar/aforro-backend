from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

from apps.products.models import Category, Product
from apps.stores.models import Store, Inventory


class OrderAPITests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='teste@example.com', 
            password='password123'
        )
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name="Tech")
        self.store = Store.objects.create(name="Test Store", location="Pune")
        self.product = Product.objects.create(
            title="Laptop", 
            price=Decimal("1000.00"), 
            category=self.category
        )
        
        self.inventory = Inventory.objects.create(
            store=self.store,
            product=self.product,
            quantity=5
        )
        
        self.url = reverse('create-order') 

    def test_create_order_success(self):
        data = {
            "store_id": self.store.id,
            "items": [{"product_id": self.product.id, "quantity_requested": 2}]
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'CONFIRMED')
        
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 3) 

    def test_create_order_out_of_stock(self):
        data = {
            "store_id": self.store.id,
            "items": [{"product_id": self.product.id, "quantity_requested": 10}]
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'REJECTED')
        
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 5)