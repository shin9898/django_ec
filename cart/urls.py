from django.urls import path
from .views import CartListView, AddToCartView, RemoveFromCartView, UpdateCartView

app_name = 'cart'
# URL configuration for the item app
urlpatterns = [
    path('list/', CartListView.as_view(), name='cart_list'),
    path('add_to_cart/<int:item_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('update/<int:item_id>/', UpdateCartView.as_view(), name='update_cart'),
]