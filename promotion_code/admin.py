from django.contrib import admin
from .models import PromotionCode, OrderPromotionCode

# Register your models here.
class OrderPromotionCodeInline(admin.TabularInline):
    model = OrderPromotionCode
    extra = 0  # 空の追加フォームを表示しない
    readonly_fields = ('promotion_code', 'used_count', 'created_at')
    fields = ('promotion_code', 'used_count', 'created_at')


@admin.register(PromotionCode)
class PromotionCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'max_uses', 'is_active', 'created_at', 'updated_at')
    search_fields = ('code',)
    list_filter = ('is_active',)
    inlines = [OrderPromotionCodeInline]
