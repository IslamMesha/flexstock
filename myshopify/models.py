from django.db import models


class ShopifyProduct(models.Model):
    title = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    vendor = models.CharField(max_length=100)
    product_type = models.CharField(max_length=100)
    product_id = models.BigIntegerField(unique=True)

    def __str__(self):
        return self.title


class ShopifyOrder(models.Model):
    user_id = models.BigIntegerField()
    order_number = models.BigIntegerField()
    name = models.CharField(max_length=100)
    note = models.CharField(max_length=100)
    gateway = models.CharField(max_length=100)

    def __str__(self):
        return str(self.order_number)
