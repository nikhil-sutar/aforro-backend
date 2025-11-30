from django.contrib import admin
from .models import Order, OrderItem
# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','user','store','status','total_amount']