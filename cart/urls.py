from django.urls import path
from .views import CartListView

app_name = 'cart'
# URL configuration for the item app
urlpatterns = [
    path('list/', CartListView.as_view(), name='cart_list'),
]