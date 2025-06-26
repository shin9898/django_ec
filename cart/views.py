from django.views import View
from django.views.generic import ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse

from .models import Cart, CartItem
from item.models import Item

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

class AddToCartView(View):
    """商品をカートに追加するビュー"""
    def post(self, request, item_id):
        """
        処理内容:
        - 商品一覧画面: quantity指定なし -> 1個追加
        - 商品詳細画面: quantity指定あり -> 指定数追加
        """
        try:
            item = get_object_or_404(Item, id=item_id, is_published=True)
            quantity = self.get_quantity_from_request(request)
            if quantity <= 0:
                messages.error(request, "数量は1以上を指定してください")
                return self.redirect_back(item_id)

            if item.stock < quantity:
                messages.error(request, f"{item.name}の在庫が不足しています（在庫: {item.stock}個）")
                return self.redirect_back(item_id)

            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key

            cart, _ = Cart.objects.get_or_create(session_key=session_key)

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                item=item,
                defaults={'quantity': quantity}
            )

            if created:
                message = f"{item.name}を{quantity}個カートに追加しました"
            else:
                new_quantity = cart_item.quantity + quantity
                if new_quantity > item.stock:
                    messages.warning(request, f"{item.name}の在庫上限を超えています（在庫: {item.stock}個）、カート内: {cart_item.quantity}個")
                    return self.redirect_back(item_id)
                cart_item.quantity = new_quantity
                cart_item.save()
                message = f"{item.name}の数量を{cart_item.quantity}個に更新しました"
            messages.success(request, message)
            return self.redirect_back(item_id)

        except Exception as e:
            messages.error(request, 'カートの追加に失敗しました')
            return self.redirect_back(item_id)

    def get_quantity_from_request(self, request):
        """リクエストから数量を取得"""
        try:
            quantity = int(request.POST.get('quantity', 1))
            return max(quantity, 1)  # 最低1個は保証
        except (ValueError, TypeError):
            return 1

    def redirect_back(self, item_id):
        """元の画面にリダイレクト"""
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return redirect(next_url)

        referer = self.request.META.get('HTTP_REFERER', '')
        if 'items/' in referer and f"/{item_id}/" not in referer:
            return redirect('item:item_list')
        else:
            return redirect('item:item_detail', pk=item_id)
    def get(self, request, item_id):
        """GETリクエストは拒否"""
        messages.error(request, "不正なリクエストです")
        return redirect('item:item_detail', pk=item_id)