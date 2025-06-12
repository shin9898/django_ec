from django.urls import path

from .views import ItemListView

app_name = 'item'
# URL configuration for the item app
urlpatterns = [
    path('', ItemListView.as_view(), name='item_list'),
]