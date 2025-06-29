from django.db import models

from item.models import Item

# Create your models here.
class Order(models.Model):
    # 顧客情報
    first_name = models.CharField(max_length=30, verbose_name='名')
    last_name = models.CharField(max_length=30, verbose_name='姓')
    email = models.EmailField(verbose_name='メールアドレス')

    # 住所情報
    postal_code = models.CharField(max_length=8, verbose_name='郵便番号')
    prefecture = models.CharField(max_length=10, verbose_name='都道府県')
    city = models.CharField(max_length=50, verbose_name='市区町村')
    address_line1 = models.CharField(max_length=100, verbose_name='番地')
    address_line2 = models.CharField(max_length=100, blank=True, null=True, verbose_name='建物名・部屋番号')

    # クレジットカード情報
    card_number = models.CharField(max_length=16, verbose_name='カード番号')
    card_expiry = models.CharField(max_length=5, verbose_name='有効期限(MM/YY)')
    card_cvv = models.CharField(max_length=4, verbose_name='CVV')
    card_holder_name = models.CharField(max_length=100, verbose_name='カード名義人')

    # 注文情報
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='注文日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    paid = models.BooleanField(default=False, verbose_name='支払済み')

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id}"

    def get_total_cost(self):
        """注文の合計額を計算"""
        return sum(item.get_cost() for item in self.items.all())

    def get_full_address(self):
        """完全な住所を取得"""
        address_parts = [
            f"〒{self.postal_code}",
            self.prefecture,
            self.city,
            self.address_line1,
        ]
        if self.address_line2:
            address_parts.append(self.address_line2)
        return ' '.join(address_parts)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='注文')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name='商品')

    # 購入時の商品情報 (Snapshot)
    item_name = models.CharField(max_length=200, verbose_name='商品名')
    item_description = models.TextField(blank=True, null=True, verbose_name='商品説明')
    item_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品価格')
    item_image = models.URLField(blank=True, null=True, verbose_name='商品画像URL')

    # 注文情報
    quantity = models.PositiveIntegerField(default=1, verbose_name='数量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='注文日時')

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return f"{self.item_name} x {self.quantity}"

    def get_cost(self):
        """小計を計算"""
        if self.item_price is None:
            return 0
        return self.item_price * self.quantity