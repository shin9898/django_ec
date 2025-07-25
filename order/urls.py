from django.urls import path

from .views import CheckoutView, OrderListView, OrderDetailView

app_name = 'order'
# URL configuration for the item app
urlpatterns = [
    path('', CheckoutView.as_view(), name='checkout'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
]