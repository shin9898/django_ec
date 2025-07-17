from django.urls import path
from .views import CartListView, AddToCartView, RemoveFromCartView, UpdateCartView

app_name = 'cart'
# URL configuration for the item app
urlpatterns = [
    path('', CartListView.as_view(), name='cart_list'),
    path('<int:item_id>/add_to_cart/', AddToCartView.as_view(), name='add_to_cart'),
    path('<int:item_id>/remove/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('<int:item_id>/update', UpdateCartView.as_view(), name='update_cart'),
]