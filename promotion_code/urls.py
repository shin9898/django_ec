from django.urls import path

from .views import ApplyPromotionCodeAjaxView

app_name = 'promotion_code'

urlpatterns = [
    path('apply/', ApplyPromotionCodeAjaxView.as_view(), name='apply'),
]