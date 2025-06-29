from django.urls import path

from .views import CheckoutView

app_name = 'order'
# URL configuration for the item app
urlpatterns = [
    path('', CheckoutView.as_view(), name='checkout'),
]