from django.db import models
from django.core.exceptions import ValidationError
import re

from order.models import Order

# Create your models here.
class PromotionCode(models.Model):
    """
    プロモーションコードを管理するモデル。
    """
    # プロモーションコード情報
    code = models.CharField(max_length=7, unique=True, verbose_name='プロモーションコード')
    discount = models.IntegerField(default=100, verbose_name='割引額')
    max_uses = models.IntegerField(default=1, verbose_name='最大使用回数') # 将来の拡張性を考慮して、max=1は設定せず
    is_active = models.BooleanField(default=True, verbose_name='有効フラグ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'promotion_codes'

    def __str__(self):
        return f"PromotionCode {self.code} - {self.discount}円割引"

    def clean(self):
        """
        バリデーションロジックを追加するためのメソッド。
        """
        # codeが7文字かつ英数字であることを確認
        if not re.match(r'^[a-zA-Z0-9]{7}$', self.code):
            raise ValidationError({"code": "プロモーションコードは英数字7桁である必要があります。"})

        # discountが100以上1000以下であることを確認
        if not (100 <= self.discount <= 1000):
            raise ValidationError({"discount": "割引額は100円以上1000円以下でなければなりません。"})

        # max_usesが1であることを確認
        if self.max_uses != 1:
            raise ValidationError({"max_uses": "最大使用回数は1でなければなりません。"})

    def is_valid(self):
        """
        プロモーションコードが有効かどうかを確認するメソッド。
        """
        if not self.is_active:
            return False


class OrderPromotionCode(models.Model):
    """
    注文とプロモーションコードの関連付けを管理する中間モデル。
    """
    promotion_code = models.ForeignKey(PromotionCode, on_delete=models.CASCADE, related_name='order_promotion_codes', verbose_name='プロモーションコード')
    order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name='注文')
    used_count = models.IntegerField(default=0, verbose_name='使用回数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時') # used_atとほぼ同義なので、created_atのみ定義


    class Meta:
        db_table = 'order_promotion_codes'
        unique_together = ('promotion_code', 'order')

    def __str__(self):
        return f"OrderPromotionCode {self.promotion_code.code} for Order {self.order.id}"
