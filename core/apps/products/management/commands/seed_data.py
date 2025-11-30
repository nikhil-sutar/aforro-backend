import random
import faker_commerce
from faker import Faker
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal

from products.models import Category, Product
from stores.models import Store, Inventory

class Command(BaseCommand):
    help = 'Seeds database with unique data using fake.unique'

    def handle(self, *args, **kwargs):
        fake = Faker()
        fake.add_provider(faker_commerce.Provider)
        
        self.stdout.write("Starting optimized data seeding...")

        try:
            with transaction.atomic():
                self.stdout.write("Cleaning old data...")
                Inventory.objects.all().delete()
                Product.objects.all().delete()
                Category.objects.all().delete()
                Store.objects.all().delete()

                self.stdout.write("Generating Categories...")
                cats = [
                    Category(name=fake.unique.ecommerce_category()) 
                    for _ in range(12)
                ]
                Category.objects.bulk_create(cats)
                all_cats = list(Category.objects.all())

                self.stdout.write("Generating 1200 Unique Products...")
                products = []
                
                for _ in range(1200):
                    products.append(Product(
                        title=fake.unique.ecommerce_name(), 
                        description=fake.text(max_nb_chars=150),
                        price=Decimal(f"{random.uniform(10, 5000):.2f}"),
                        category=random.choice(all_cats)
                    ))
                
                Product.objects.bulk_create(products)
                all_products = list(Product.objects.all())

                self.stdout.write("Generating 25 Stores with unique locations...")
                stores = []
                created_store_pairs = set()
                
                while len(stores) < 25:
                    base_name = fake.company() 
                    city = fake.city()
                    pair = (base_name, city)
                    
                    if pair in created_store_pairs:
                        continue 
                    created_store_pairs.add(pair)
                    
                    stores.append(Store(
                        name=base_name,
                        location=city
                    ))
                
                Store.objects.bulk_create(stores)
                all_stores = list(Store.objects.all())

                self.stdout.write("Generating Inventory...")
                inventory_list = []

                for store in all_stores:
                    store_products = random.sample(all_products, k=350)
                    for prod in store_products:
                        inventory_list.append(Inventory(
                            store=store,
                            product=prod,
                            quantity=random.randint(0, 100)
                        ))
                
                Inventory.objects.bulk_create(inventory_list)

                self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

        except Exception as e:
            if "UniquenessException" in str(e):
                self.stdout.write(self.style.WARNING("Stopped early: Faker ran out of unique names. Try reducing product count."))
            else:
                self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))