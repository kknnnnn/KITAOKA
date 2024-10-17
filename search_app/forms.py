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
