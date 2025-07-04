import json
from django.http import JsonResponse
from django.views.generic import View
from django.db import transaction
from promotion_code.models import PromotionCode, OrderPromotionCode, Order

# Create your views here.
class ApplyPromotionCodeAjaxView(View):
    """
    プロモーションコードを適用するためのAjaxビュー
    """
    def post(self, request, *args, **kwargs):
        """
        POSTリクエストを処理し、プロモーションコードを適用する。
        """
        data = json.loads(request.body)
        code = data.get('promotion_code')
        response_data = {}

        if not code:
            return JsonResponse({'success': False, 'message': 'プロモーションコードが入力されていません。'}, status=400)

        try:
            cart_id = request.session.get('cart_id')
            user_order = Order.objects.filter(cart_id=cart_id)
            promo_code_obj = PromotionCode.objects.get(code=code)
            if not promo_code_obj.is_valid():
                response_data = {'success': False, 'message': 'このプロモーションコードは無効です。'}
                return JsonResponse(response_data, status=400)

            with transaction.atomic():
                response_data = {
                    'success': True,
                    'message': f"プロモーションコード'{code}'が適用されました。{promo_code_obj.discount}円割引されます。",
                    'discount_amount': promo_code_obj.discount,
                    'new_total_price': Order.total_price - promo_code_obj.discount
                }
                return JsonResponse(response_data, status=200)
        except PromotionCode.DoesNotExist:
            response_data = {'success': False, 'message': '入力されたプロモーションコードが見つかりません。'}
            return JsonResponse(response_data, status=404)
        except Exception as e:
            response_data = {'success': False, 'message': f"エラーが発生しました: {str(e)}"}
            return JsonResponse(response_data, status=500)
