from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction

from promotion_code.models import PromotionCode
from cart.models import Cart
from order.forms import OrderForm

# Create your views here.
class ApplyPromotionCodeView(View):
    """
    プロモーションコードを適用するための同期処理ビュー。
    POSTリクエストでコードを受け取り、カートに適用後、カートページを再表示する。
    """
    def post(self, request, *args, **kwargs):
        """
        POSTリクエストを処理し、入力されたプロモーションコードをカートに適用する。
        検証に失敗した場合やエラーが発生した場合はエラーメッセージを表示し、
        適用に成功した場合は成功メッセージを表示してカートページを再レンダリングする。

        """
        code = request.POST.get('promotion_code', '').strip()
        customer_form = OrderForm(request.POST)

        if not code:
            messages.error(request, 'クーポンコードが入力されていません。')
            return self._render_cart_list(request, customer_form, code)

        session_key = request.session.session_key
        if not session_key:
            messages.error(request, 'カート情報が見つかりません。セッションを再開してください。')
            return self._render_cart_list(request, customer_form, code)

        try:
            cart = Cart.objects.get(session_key=session_key)
        except Cart.DoesNotExist:
            messages.error(request, 'カートが見つかりません。')
            return self._render_cart_list(request, customer_form, code)

        try:
            promo_code_obj = PromotionCode.objects.get(code=code)

            if not promo_code_obj.is_valid():
                messages.error(request, 'このクーポンは現在使用できません。')
                return self._render_cart_list(request, customer_form, code)

            if cart.discount_amount > 0:
                messages.warning(request, 'このカートには既にクーポンが適用されています。')
                return self._render_cart_list(request, customer_form, code)

            with transaction.atomic():
                cart.discount_amount = promo_code_obj.discount
                cart.save()
                messages.success(request, f"クーポンコード'{code}'が適用されました。{promo_code_obj.discount}円割引されます！")

                return self._render_cart_list(request, customer_form, code)
        except PromotionCode.DoesNotExist:
            messages.error(request, '入力されたクーポンコードが見つかりません。')
            return self._render_cart_list(request, customer_form, code)
        except Exception as e:
            messages.error(request, f"エラーが発生しました: {str(e)}")
            return self._render_cart_list(request, customer_form, code)

    def get(self, request, *args, **kwargs):
        return redirect('cart:cart_list')

    def _render_cart_list(self, request, customer_form=None, code=None):
        session_key = request.session.session_key
        cart = None
        cart_items = []
        if code:
            request.session['promotion_code'] = code
        if session_key:
            try:
                cart = Cart.objects.prefetch_related('cart_items__item').get(session_key=session_key)
                cart_items = cart.cart_items.all()
            except Cart.DoesNotExist:
                pass

        context = {
            'cart': cart,
            'cart_items': cart_items,
            'form': customer_form,
            'promotion_code': code or request.session.get('promotion_code', '')
        }
        return render(request, 'cart/cart_list.html', context)