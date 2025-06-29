from django.contrib import admin
from .models import Order, OrderItem

# OrderItemのインライン表示
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # 空の追加フォームを表示しない
    readonly_fields = (
        'item_name', 'item_description', 'item_price', 'item_image',
        'quantity', 'get_cost_display',
        )
    fields = ('item', 'item_name', 'item_price', 'quantity', 'get_cost_display')

    def get_cost_display(self, obj):
        """小計を表示"""
        cost = obj.get_cost()
        return f"¥{cost:,}" if cost else "¥0"
    get_cost_display.short_description = '小計'

# Order管理画面
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'get_customer_name',
        'email',
        'username',
        'get_total_cost_display',
        'paid',
        'created_at'
    ]
    list_filter = [
        'paid',
        'created_at',
        'prefecture'
    ]
    search_fields = [
        'email',
        'first_name',
        'last_name',
        'username',
        'id'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'get_total_cost_display',
        'get_full_address'
    ]
    fieldsets = (
        ('注文情報', {
            'fields': ('paid',)  # ← id, created_at, updated_at, get_total_cost_display を削除
        }),
        ('顧客情報', {
            'fields': ('first_name', 'last_name', 'email', 'username')
        }),
        ('住所情報', {
            'fields': ('postal_code', 'prefecture', 'city', 'address_line1', 'address_line2')  # ← get_full_address を削除
        }),
        ('決済情報', {
            'fields': ('card_number', 'card_expiry', 'card_cvv', 'card_holder_name'),
            'classes': ('collapse',)  # 折りたたみ表示
        }),
    )
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'  # 日付による階層フィルタ

    def get_customer_name(self, obj):
        """顧客名を表示"""
        return f"{obj.last_name} {obj.first_name}"
    get_customer_name.short_description = '顧客名'

    def get_total_cost_display(self, obj):
        """合計金額を表示"""
        total = obj.get_total_cost()
        return f"¥{total:,}" if total else "¥0"
    get_total_cost_display.short_description = '合計金額'

# OrderItem管理画面（個別管理用）
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order',
        'item_name',
        'item_price',
        'quantity',
        'get_cost_display',
        'created_at'
    ]
    list_filter = [
        'created_at',
        'item_name'
    ]
    search_fields = [
        'order__id',
        'order__email',
        'order__username',
        'item_name'
    ]
    readonly_fields = [
        'item_name', 'item_description', 'item_price', 'item_image',
        'created_at',
        'get_cost_display'
    ]

    def get_cost_display(self, obj):
        """小計を表示"""
        cost = obj.get_cost()
        return f"¥{cost:,}" if cost else "¥0"
    get_cost_display.short_description = '小計'
