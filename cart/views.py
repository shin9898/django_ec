from django.shortcuts import render
from django.views.generic import ListView

from .models import Cart, CartItem

# Create your views here.
class CartListView(ListView):
    model = CartItem
    template_name = 'cart/cart_list.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        # セッションキーでカートを取得
        session_key = self.request.session.session_key
        if not session_key:
            # セッションが存在しない場合は空のクエリセットを返す
            return CartItem.objects.none()

        try:
            cart = Cart.objects.get(session_key=session_key)
            return cart.cart_items.select_related('item').all()
        except Cart.DoesNotExist:
            return CartItem.objects.none()

    def get_context_data(self, **kwargs):
        """データ取得とコンテキスト準備"""
        context = super().get_context_data(**kwargs)

        session_key = self.request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.get(session_key=session_key)
                context['total_price'] = cart.total_price  # @propertyを呼び出し
                context['cart'] = cart
            except Cart.DoesNotExist:
                context['total_price'] = 0

        return context
