from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from basicauth.decorators import basic_auth_required

from .models import Item
from .forms import ItemForm

# Create your views here.
class ItemListView(ListView):
    model = Item
    template_name = 'item/item_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_published=True).order_by('-created_at')
        return queryset


class ItemDetailView(DetailView):
    model = Item
    template_name = 'item/item_detail.html'
    context_object_name = 'item'

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

@method_decorator(basic_auth_required, name='dispatch')
class ManageItemListView(ListView):
    model = Item
    template_name = 'item/manage_item_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        queryset = super().get_queryset()  # デフォルトのクエリセット（全商品）を取得
        return queryset.order_by('-created_at')  # 新しい順に並べ替え

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 統計データを計算
        total_items = Item.objects.count()
        published_items = Item.objects.filter(is_published=True).count()
        low_stock_items = Item.objects.filter(stock__lte=5, stock__gt=0).count()  # 1-5個
        out_of_stock_items = Item.objects.filter(stock=0).count()  # 0個

        # コンテキストに追加
        context.update({
            'total_items': total_items,
            'published_items': published_items,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
        })

        return context

@method_decorator(basic_auth_required, name='dispatch')
class ManageItemCreateView(CreateView):
    model = Item
    template_name = 'item/manage_item_form.html'
    fields = ['name', 'description', 'price', 'stock', 'sku', 'image', 'is_published']
    success_url = reverse_lazy('item:manage_item_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'create'
        context['title'] = '商品作成'
        return context

@method_decorator(basic_auth_required, name='dispatch')
class ManageItemUpdateView(UpdateView):
    model = Item
    template_name = 'item/manage_item_form.html'
    fields = ['name', 'description', 'price', 'stock', 'sku', 'image', 'is_published']
    success_url = reverse_lazy('item:manage_item_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'update'
        context['title'] = '商品更新'
        return context

@method_decorator(basic_auth_required, name='dispatch')
class ManageItemDeleteView(DeleteView):
    model = Item
    success_url = reverse_lazy('item:manage_item_list')

    def get(self, request, *args, **kwargs):
        return redirect(self.success_url)

    def delete(self, request, *args, **kwargs):
        # 削除対象のオブジェクトを取得
        self.object = self.get_object()
        # 削除前に商品名を保存
        item_name = self.object.name
        # 親クラス(DeleteView)の削除処理を実行
        response = super().delete(request, *args, **kwargs)
        # 削除成功のFlashメッセージを追加
        messages.success(
            self.request,
            f'商品「{item_name}」を削除しました。',
        )
        return response

    def post(self, request, *args, **kwargs):
        # POSTリクエストでの削除を許可
        return super().post(request, *args, **kwargs)