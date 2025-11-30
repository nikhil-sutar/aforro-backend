from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.products.models import Category, Product
from apps.stores.models import Store, Inventory

class SearchAPITests(APITestCase):
    
    def setUp(self):
        self.cat = Category.objects.create(name="SmartPhones")
        self.store = Store.objects.create(name="Test Store", location="Pune")
        
        self.p1 = Product.objects.create(title="iPhone 15", price=Decimal("80000"), category=self.cat)
        self.p2 = Product.objects.create(title="Samsung S24", price=Decimal("70000"), category=self.cat)
        
        Inventory.objects.create(store=self.store, product=self.p1, quantity=10)

        self.url = reverse('product-search')

    def test_search_by_keyword(self):
        response = self.client.get(self.url, {'search': 'iPhone'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'iPhone 15')

    def test_filter_in_stock(self):
        response = self.client.get(self.url, {
            'store_id': self.store.id,
            'in_stock': 'true'
        })
        
        results = response.data['results']
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.p1.id)
        
        self.assertEqual(results[0]['inventory_quantity'], 10)