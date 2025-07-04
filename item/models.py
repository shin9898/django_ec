from django.db import models

# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.IntegerField(default=0)
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True) # 商品コード/SKU
    stock = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True) # 商品の公開非公開を管理
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'items'
        ordering = ['-created_at']