from django.db import models
from store.models import Product,Variation
from accounts.models import Account
from django.utils import timezone


# Create your models here.

class Cart(models.Model):
    cart_id=models.CharField(max_length=250,blank=True)
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    user=models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation=models.ManyToManyField(Variation, blank=True)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE, null=True)
    quantity=models.IntegerField()
    created_at =models.DateTimeField(auto_now_add=True)
    is_active=models.BooleanField(default=True)

    class Meta:
        db_table = 'cart_item'

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return str(self.product)
    