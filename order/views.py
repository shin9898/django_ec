from django.views.generic import CreateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

from cart.models import Cart
from .forms import OrderForm
from .models import Order, OrderItem

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
            self.cart = Cart.objects.get(session_key=request.session_key)
            self.cart_items = self.cart.items.all()
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
        self.object = form.save(commit=False)
        self.object.paid = True
        self.object.save()
        self.create_order_items()
        self.cart.delete()
        messages.success(self.request, '購入ありがとうございます')
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
