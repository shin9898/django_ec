from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'email',
            'username',
            'postal_code',
            'prefecture',
            'city',
            'address_line1',
            'address_line2',
            'card_number',
            'card_expiry',
            'card_cvv',
            'card_holder_name'
        ]

    def clean_postal_code(self):
        """郵便番号のバリデーション"""
        postal_code = self.cleaned_data.get('postal_code')
        if postal_code:
            cleaned = postal_code.replace('-', '')
            if not cleaned.isdigit() or len(cleaned) != 7:
                raise forms.ValidationError('郵便番号は123-4567の形式で入力してください')
            return f"{cleaned[:3]}-{cleaned[3:]}"
        return postal_code

    def clean_card_number(self):
        """カード番号のバリデーション"""
        card_number = self.cleaned_data.get('card_number')
        if card_number:
            cleaned = card_number.replace(' ', '').replace('-', '')
            if not cleaned.isdigit() or len(cleaned) not in [15, 16]:
                raise forms.ValidationError('カード番号は15桁または16桁の数字で入力してください')
            return cleaned
        return card_number

    def clean_card_expiry(self):
        """有効期限のバリデーション"""
        card_expiry = self.cleaned_data.get('card_expiry')
        if card_expiry:
            if '/' not in card_expiry or len(card_expiry) != 5:
                raise forms.ValidationError('有効期限はMM/YY形式で入力してください')
            try:
                month, year = card_expiry.split('/')
                if not (1 <= int(month) <= 12):
                    raise forms.ValidationError('月は01-12の範囲で入力してください')
                if len(year) != 2 or not year.isdigit():
                    raise forms.ValidationError('年は2桁で入力してください')
            except (ValueError, TypeError):
                raise forms.ValidationError('有効期限はMM/YY形式で入力してください')
        return card_expiry

    def clean_card_cvv(self):
        """CVVのバリデーション"""
        card_cvv = self.cleaned_data.get('card_cvv')
        if card_cvv:
            if not card_cvv.isdigit() or len(card_cvv) not in [3, 4]:
                raise forms.ValidationError('CVVは3桁または4桁の数字で入力してください')
        return card_cvv
