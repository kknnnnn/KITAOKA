from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'category'  # 明示的にテーブル名を指定

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)

    # 新しい画像フィールド
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    class Meta:
        db_table = 'product'  # 明示的にテーブル名を指定

    def __str__(self):
        return self.name
    
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')  # ユーザーごとに重複しないようにする
        
class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ユーザーごとに検索履歴を保存
    query = models.CharField(max_length=255, blank=True)  # 検索キーワード
    category_name = models.CharField(max_length=255, blank=True)  # カテゴリ名
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 最小価格
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 最大価格
    created_at = models.DateTimeField(auto_now_add=True)  # 検索日時

    class Meta:
        ordering = ['-created_at']  # 最新順
    
class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} - {self.user.username}"
    