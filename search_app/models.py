from django.db import models
from django.contrib.auth.models import User
import datetime


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
    
class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # 合計金額
    purchased_at = models.DateTimeField(auto_now_add=True)  # 購入日時
    used_points = models.PositiveIntegerField(default=0)  # 使用したポイントフィールドを追加

    def __str__(self):
        return f"Purchase {self.id} by {self.user.username} on {self.purchased_at.strftime('%Y-%m-%d %H:%M:%S')}"

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=81)
    quantity = models.PositiveIntegerField()  # 購入数量
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 単価

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"

class Point(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # ユーザーごとに1つのポイントデータ
    balance = models.PositiveIntegerField(default=0)  # 現在のポイント残高

    def __str__(self):
        return f"{self.user.username}: {self.balance} points"
