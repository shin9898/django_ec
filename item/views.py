from django.shortcuts import render
from django.views.generic.list import ListView

from .models import Item

# Create your views here.
class ItemListView(ListView):
    model = Item
    template_name = 'item/item_list.html'
    context_object_name = 'items'  # テンプレートで使用するコンテキスト変数名
    paginate_by = 8  # 1ページあたりのアイテム数

    def get_queryset(self):
        queryset = super().get_queryset() # デフォルトのクエリセット（全商品）を取得
        queryset = queryset.filter(is_published=True).order_by('-created_at') # 公開中かつ新しい順にフィルタ
        return queryset
