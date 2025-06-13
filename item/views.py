from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Item

# Create your views here.
class ItemListView(ListView):
    model = Item
    template_name = 'item/item_list.html'
    context_object_name = 'items'  # テンプレートで使用するコンテキスト変数名
    paginate_by = 20  # 1ページあたりのアイテム数

    def get_queryset(self):
        queryset = super().get_queryset() # デフォルトのクエリセット（全商品）を取得
        queryset = queryset.filter(is_published=True).order_by('-created_at') # 公開中かつ新しい順にフィルタ
        return queryset


class ItemDetailView(DetailView):
    model = Item
    template_name = 'item/item_detail.html'
    context_object_name = 'item'  # テンプレートで使用するコンテキスト変数名

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 関連商品を取得
        related_items = Item.objects.filter(
            is_published=True
        ).exclude(
            pk=self.object.pk  # 現在のアイテムを除外
        ).order_by(
            '-created_at' # 新しい順に並べ替え
        )[:4] # 最大4件取得

        context['related_items'] = related_items
        return context