from django.contrib import admin
from .models import Category, Product, Supplier, InventoryMovement


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Supplier)
admin.site.register(InventoryMovement)
