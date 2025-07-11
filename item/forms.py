from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price', 'image', 'sku', 'stock', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'price': forms.NumberInput(attrs={'min': '1'}),
        }
        labels = {
            'name': '商品名',
            'description': '商品説明',
            'price': '価格',
            'image': '商品画像',
            'sku': '商品コード/SKU',
            'stock': '在庫数',
            'is_published': '公開状態',
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError('価格は1円以上で入力してください。')
        return price