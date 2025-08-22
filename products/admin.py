from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "price", "discount", "stock", "image_url", "created_at")
    search_fields = ("name","price")