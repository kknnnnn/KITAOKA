from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Favorite
from .forms import ProductForm, SearchForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import CustomPasswordChangeForm
from django.http import JsonResponse
from decimal import Decimal
from django.db.models import Count

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('search_view')
        else:
            print("フォームエラー:", form.errors)  # フォームエラーを出力
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # ユーザーのお気に入りを取得
    favorites = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True) if request.user.is_authenticated else []

    # 商品のお気に入り数を全ユーザーでカウント
    favorites_count = Favorite.objects.filter(product=product).count()

    # 同じカテゴリの商品を取得（検索商品は除外）
    same_category_products = Product.objects.filter(
        category=product.category
    ).exclude(pk=product.pk)[:5]  # 最大5件

    # 類似価格帯の商品を取得（±20%の価格範囲内、検索商品は除外）
    price_min = product.price * Decimal('0.8')
    price_max = product.price * Decimal('1.2')
    similar_price_products = Product.objects.filter(
        price__gte=price_min,
        price__lte=price_max
    ).exclude(pk=product.pk)[:5]

    # コンテキストにレコメンド商品リストを追加
    context = {
        'product': product,
        'favorites': favorites,
        'favorites_count': favorites_count,
        'same_category_products': same_category_products,
        'similar_price_products': similar_price_products,
    }
    
    return render(request, 'product_detail.html', context)

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)  # request.FILES を追加
        if form.is_valid():
            form.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form, 'product': product})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('search_view')
    return render(request, 'product_confirm_delete.html', {'product': product})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def search_view(request):
    form = SearchForm(request.GET or None)
    
    # クエリセットの初期化
    results = Product.objects.all()  # すべてのProductを取得
    
    # 検索条件をURLパラメータから取得
    query = request.GET.get('query', '').strip()
    category_name = request.GET.get('category', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    sort_by = request.GET.get('sort', 'name')

    # フィルタリング処理
    if query:  # クエリがある場合
        results = results.filter(name__icontains=query)

    if category_name:  # カテゴリが指定されている場合
        try:
            category = Category.objects.get(name=category_name)
            results = results.filter(category_id=category.id)
        except Category.DoesNotExist:
            results = results.none()  # 存在しないカテゴリの場合、結果を空にする

    # min_price と max_price の処理
    if min_price:  # min_price が指定されている場合
        try:
            min_price_value = float(min_price)
            results = results.filter(price__gte=min_price_value)
        except ValueError:
            pass  # 無効な値は無視

    if max_price:  # max_price が指定されている場合
        try:
            max_price_value = float(max_price)
            results = results.filter(price__lte=max_price_value)
        except ValueError:
            pass  # 無効な値は無視

    # 並び替え処理
    if sort_by == 'price_asc':
        results = results.order_by('price')
    elif sort_by == 'price_desc':
        results = results.order_by('-price')
    elif sort_by == 'popularity':  # 人気順の並び替え
        results = results.order_by('-favorite_count')  # 仮にfavorite_countフィールドが人気を表すとする
    else:  # デフォルトの並び替え（名前順）
        results = results.order_by('name')

    # ページネーション
    paginator = Paginator(results, 10)  # 1ページあたりのアイテム数
    page_number = request.GET.get('page', 1)  # デフォルトは1ページ目
    page_obj = paginator.get_page(page_number)

    # 人気ランキング用（お気に入り数が多いTOP3の商品を取得）
    popular_products = (
        Product.objects.annotate(favorites_count=Count('favorite'))
        .order_by('-favorites_count')[:3]
    )

    # テンプレートへのコンテキスト渡し
    context = {
        'form': form,
        'page_obj': page_obj,
        'query': query,
        'category_name': category_name,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'popular_products': popular_products,  # 人気ランキング用のコンテキスト
    }

    return render(request, 'search.html', context)

@login_required
def mypage_view(request):
    # ユーザーの情報などを表示する
    return render(request, 'mypage.html')

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'templates/password_change.html'  # カスタムテンプレート
    success_url = reverse_lazy('mypage')  # パスワード変更後のリダイレクト先

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # セッションを更新
            messages.success(request, 'パスワードが変更されました。')
            return redirect('mypage')  # マイページへリダイレクト
    else:
        form = CustomPasswordChangeForm(user=request.user)
    
    return render(request, 'password_change.html', {'form': form})

@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    favorite = Favorite.objects.filter(user=request.user, product=product).first()
    
    if favorite:
        favorite.delete()  # お気に入りから削除
        messages.success(request, 'お気に入りから削除しました。')
    else:
        Favorite.objects.create(user=request.user, product=product)  # お気に入りに追加
        messages.success(request, 'お気に入りに追加しました。')

    return redirect('product_detail', pk=product.pk)


@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    return render(request, 'favorites_list.html', {'favorites': favorites})
