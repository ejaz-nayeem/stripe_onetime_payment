from django.contrib import admin

# Register your models here.
# payments/admin.py

from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'price', 'status', 'created_at', 'stripe_checkout_id')
    list_filter = ('status', 'created_at')