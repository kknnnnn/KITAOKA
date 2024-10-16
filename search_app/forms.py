from django import forms
from .models import Product

class SearchForm(forms.Form):
    query = forms.CharField(
        label='検索キーワード',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '検索したいキーワードを入力'})
    )

    def clean_query(self):
        query = self.cleaned_data.get('query')
        if query and len(query) < 3:  # キーワードが3文字未満の場合エラー
            raise forms.ValidationError('検索キーワードは3文字以上で入力してください。')
        return query

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '商品名を入力'}),
            'description': forms.Textarea(attrs={'placeholder': '商品の説明を入力', 'rows': 4}),
            'price': forms.NumberInput(attrs={'placeholder': '価格を入力'}),
            'category': forms.Select(),  # カテゴリ選択用のウィジェット
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 2:  # 商品名が2文字未満の場合エラー
            raise forms.ValidationError('商品名は2文字以上で入力してください。')
        return name

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:  # 価格が0円以下の場合エラー
            raise forms.ValidationError('価格は0円以上でなければなりません。')
        return price
