from django.urls import path

from .views import ApplyPromotionCodeView

app_name = 'promotion_code'

urlpatterns = [
    path('apply/', ApplyPromotionCodeView.as_view(), name='apply'),
]