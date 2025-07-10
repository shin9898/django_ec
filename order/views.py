from django.views.generic import CreateView, ListView, DetailView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.db.models import Prefetch


from basicauth.decorators import basic_auth_required
from cart.models import Cart
from .forms import OrderForm
from .models import Order, OrderItem, PromotionCode
from .utils import send_order_confirmation_email

# Create your views here.
class CheckoutView(CreateView):
    """チェックアウト処理を行うCBV"""
    model = Order
    form_class = OrderForm
    template_name = 'cart/cart_list.html'
    success_url = reverse_lazy('item:item_list')

    def dispatch(self, request, *args, **kwargs):
        """リクエスト処理前の共通チェック"""
        try:
            self.cart = Cart.objects.get(session_key=request.session.session_key)
            self.cart_items = self.cart.cart_items.all()
        except Cart.DoesNotExist:
            messages.error(request, 'カートが空です')
            return redirect('item:item_list')

        if not self.cart_items:
            messages.error(request, 'カートに商品がありません')
            return redirect('item:item_list')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """テンプレートに渡すコンテキストデータ"""
        context = super().get_context_data(**kwargs)
        context.update({
            'cart': self.cart,
            'cart_items': self.cart_items,
        })
        return context

    def form_valid(self, form):
        """フォーム送信成功時の処理"""
        # 在庫チェック・更新
        if not self.update_stock():
            return self.form_invalid(form)
        # 注文を保存
        self.object = form.save(commit=False)
        self.object.paid = True

        promotion_code_str = self.request.session.get('promotion_code')
        if promotion_code_str:
            try:
                promo = PromotionCode.objects.get(code=promotion_code_str, is_active=True, is_used=False)
                self.object.promotion_code = promo
                promo.is_used = True
                promo.save()
            except PromotionCode.DoesNotExist:
                messages.warning(self.request, "クーポンコードが無効またはすでに使用されているか、存在しないコードです。")

        self.object.save()

        # 注文アイテム作成 (Snapshotパターン)
        self.create_order_items()

        # メール送信処理
        email_sent = send_order_confirmation_email(self.object)

        # カート削除
        self.cart.delete()

        # メール送信結果に応じたメッセージ表示
        if email_sent:
            messages.success(self.request, 'ご購入ありがとうございます。確認メールをお送りしました。')
        else:
            messages.success(self.request, '購入ありがとうございます。')
            messages.warning(self.request, 'メール送信でエラーが発生しました。お問い合わせください。')

        return super().form_valid(form)

    def form_invalid(self, form):
        """フォームにエラーがある場合の処理"""
        messages.error(self.request, 'フォームに不正な値があります。確認してください')
        return super().form_invalid(form)

    def create_order_items(self):
        """注文アイテムを作成(Snapshotパターン)"""
        for cart_item in self.cart_items:
            OrderItem.objects.create(
                order=self.object,
                item=cart_item.item,
                item_name=cart_item.item.name,
                item_description=cart_item.item.description or '',
                item_price=cart_item.item.price,
                item_image=cart_item.item.image.url if cart_item.item.image else None,
                quantity=cart_item.quantity
            )

    def update_stock(self):
        """在庫を更新する"""
        try:
            with transaction.atomic():
                for cart_item in self.cart_items:
                    product = cart_item.item
                    quantity = cart_item.quantity
                    product = product.__class__.objects.select_for_update().get(id=product.id)

                    # 在庫チェック
                    if product.stock < quantity:
                        messages.error(self.request, f'{product.name}の在庫が不足しています。')
                        return False
                    # 在庫を減らす
                    product.stock -= quantity
                    product.save()
            return True
        except Exception as e:
            messages.error(self.request, f"在庫更新中にエラーが発生しました: {str(e)}")
            return False

@method_decorator(basic_auth_required, name='dispatch')
class OrderListView(ListView):
    model = Order
    template_name = 'order/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # URLパラメータから期間を取得
        period = self.request.GET.get('period', '3months')

        # 期間に応じた日数を設定
        if period == '1month':
            days = 30
        elif period == '6months':
            days = 180
        elif period == '1year':
            days = 365
        elif period == 'all':
            days = None
        else:  # 3months (デフォルト)
            days = 90

        # クエリセットを構築
        queryset = Order.objects.filter(paid=True)

        if days is not None:
            start_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(created_at__gte=start_date)

        queryset = queryset.prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('item'))
        ).order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 日付でグループ化
        orders_by_date = {}
        for order in context['orders']:
            date_key = order.created_at.date()
            if date_key not in orders_by_date:
                orders_by_date[date_key] = []
            orders_by_date[date_key].append(order)

        context['orders_by_date'] = dict(sorted(orders_by_date.items(), reverse=True))
        return context


@method_decorator(basic_auth_required, name='dispatch')
class OrderDetailView(DetailView):
    model = Order
    template_name = 'order/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        """支払済み注文のみ表示"""
        return Order.objects.filter(paid=True).prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('item'))
        )

    def get_context_data(self, **kwargs):
        """追加のコンテキストデータ"""
        context = super().get_context_data(**kwargs)
        context['total_items'] = self.object.items.count()
        return context
