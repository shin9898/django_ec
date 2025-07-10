from django.db import models
from django.core.exceptions import ValidationError
import re

# Create your models here.
class PromotionCode(models.Model):
    """
    プロモーションコードを管理するモデル。
    """
    # プロモーションコード情報
    code = models.CharField(max_length=7, unique=True, verbose_name='プロモーションコード')
    discount = models.IntegerField(default=100, verbose_name='割引額')
    is_active = models.BooleanField(default=True, verbose_name='有効フラグ')
    is_used = models.BooleanField(default=False, verbose_name='使用済')
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

    def is_valid(self):
        """
        プロモーションコードが有効かどうかを確認するメソッド。
        """
        return self.is_active and not self.is_used
