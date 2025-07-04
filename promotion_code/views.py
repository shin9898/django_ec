import json
from django.http import JsonResponse
from django.views.generic import View
from django.db import transaction
from promotion_code.models import PromotionCode, OrderPromotionCode, Order

# Create your views here.
class ApplyPromotionCodeAjaxView(View):
    pass