from django.views import View
from django.views.generic import ListView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from .models import Cart, CartItem
from item.models import Item
from order.forms import OrderForm

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
                context['total_items_count'] = cart.total_items_count
            except Cart.DoesNotExist:
                context['total_price'] = 0
                context['total_items_count'] = 0
                context['cart'] = None
        else:
            context['total_price'] = 0
            context['total_items_count'] = 0
            context['cart'] = None

        context['form'] = OrderForm()

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

            if not item.is_published:
                messages.error(request, "この商品は現在購入できません")
                return self.redirect_back(item_id)

            if item.stock <= 0:
                messages.error(request, f"{item.name}は在庫切れです")
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

class RemoveFromCartView(View):
    """カートから商品を削除"""
    def post(self, request, item_id):
        try:
            session_key = request.session.session_key
            if not session_key:
                messages.error(request, "カートが見つかりません")
                return redirect('cart:cart_list')
            cart = get_object_or_404(Cart, session_key=session_key)
            cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)

            # 削除前に商品名を保存（メッセージ用）
            item_name = cart_item.item.name
            quantity = cart_item.quantity

            cart_item.delete()
            messages.success(request, f"{item_name} ({quantity}個)をカートから削除しました")
            return redirect('cart:cart_list')
        except Exception as e:
            messages.error(request, 'カートからの削除に失敗しました')
            return redirect('cart:cart_list')

    def get(self, request, item_id):
        """GETリクエストは拒否"""
        messages.error(request, "不正なリクエストです")
        return redirect('cart:cart_list')

class UpdateCartView(View):
    """カート内商品の数量を更新"""
    def post(self, request, item_id):
        try:
            session_key = request.session.session_key
            if not session_key:
                messages.error(request, 'カートが見つかりません')
                return redirect('cart:cart_list')

            cart = get_object_or_404(Cart, session_key=session_key)
            cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)

            try:
                new_quantity = int(request.POST.get('quantity', 1))
            except (ValueError, TypeError):
                messages.error(request, '無効な数量です')
                return redirect('cart:cart_list')

            if new_quantity < 0:
                messages.error(request, '数量は0以上を指定してください')
                return redirect('cart:cart_list')

            if new_quantity == 0:
                item_name = cart_item.item.name
                cart_item.delete()
                messages.success(request, f'{item_name}をカートから削除しました')
                return redirect('cart:cart_list')

            if new_quantity > cart_item.item.stock:
                messages.warning(request, f"{cart_item.item.name}の在庫が不足しています（在庫: {cart_item.item.stock}個）")
                return redirect('cart:cart_list')

            old_quantity = cart_item.quantity
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f"{cart_item.item.name}の数量を{old_quantity}から{new_quantity}に更新しました")
            return redirect('cart:cart_list')
        except Exception as e:
            messages.error(request, '数量の更新に失敗しました')
            return redirect('cart:cart_list')

    def get(self, request, item_id):
        """GETリクエストは拒否"""
        messages.error(request, "不正なリクエストです")
        return redirect('cart:cart_list')