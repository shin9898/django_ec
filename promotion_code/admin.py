from django.contrib import admin
from .models import PromotionCode

# Register your models here.
@admin.register(PromotionCode)
class PromotionCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'is_active', 'is_used', 'created_at', 'updated_at')
    search_fields = ('code',)
    list_filter = ('is_active',)