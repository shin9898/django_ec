from django.urls import path

from .views import ItemListView, ItemDetailView

app_name = 'item'
# URL configuration for the item app
urlpatterns = [
    path('items/', ItemListView.as_view(), name='item_list'),
    path('items/<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
]