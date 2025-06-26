from django.urls import path
from .views import CartListView, AddToCartView

app_name = 'cart'
# URL configuration for the item app
urlpatterns = [
    path('list/', CartListView.as_view(), name='cart_list'),
    path('add_to_cart/<int:item_id>/', AddToCartView.as_view(), name='add_to_cart'),
]