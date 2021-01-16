from django.contrib import admin
from myshopify.models import ShopifyOrder, ShopifyProduct

admin.site.register(ShopifyOrder)
admin.site.register(ShopifyProduct)
