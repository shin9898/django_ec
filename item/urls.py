from django.urls import path

from .views import ItemListView, ItemDetailView, ManageItemListView, ManageItemCreateView, ManageItemUpdateView, ManageItemDeleteView

app_name = 'item'
# URL configuration for the item app
urlpatterns = [
    path('', ItemListView.as_view(), name='item_list'),
    path('<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
    path('manage/', ManageItemListView.as_view(), name='manage_item_list'),
    path('manage/create/', ManageItemCreateView.as_view(), name='manage_item_create'),
    path('manage/<int:pk>/update/', ManageItemUpdateView.as_view(), name='manage_item_update'),
    path('manage/<int:pk>/delete', ManageItemDeleteView.as_view(), name='manage_item_delete'),
]