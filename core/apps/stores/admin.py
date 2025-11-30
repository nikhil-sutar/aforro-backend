from django.contrib import admin
from .models import Store, Inventory
# Register your models here.

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['id','name','location']

@admin.register(Inventory)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['id','store','product','quantity']
