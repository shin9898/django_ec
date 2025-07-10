from django.db import models

from item.models import Item

# Create your models here.
class Cart(models.Model):
    session_key = models.CharField(max_length=40, unique=True, verbose_name='セッションキー')
    discount_amount = models.IntegerField(default=0, verbose_name='割引額')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Cart {self.session_key}"

    @property
    def total_items_count(self):
        """カート内の総商品数"""
        return sum(item.quantity for item in self.cart_items.all())

    @property
    def total_price(self):
        """カート内の総価格(割引適用後)"""
        items_total = sum(item.total_price for item in self.cart_items.all())
        return max(0, items_total - self.discount_amount)

    @property
    def original_total_price(self):
        """カート内の総価格(割引適用前)"""
        return sum(item.total_price for item in self.cart_items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cart_items'
        unique_together = ('cart', 'item')
        ordering = ['added_at']

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.item.price * self.quantity