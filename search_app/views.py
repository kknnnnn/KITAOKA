from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Favorite, Purchase
from .forms import ProductForm, SearchForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import CustomPasswordChangeForm
from django.http import JsonResponse, HttpResponseNotAllowed
from decimal import Decimal
from django.db.models import Count
from collections import defaultdict

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
    # 検索フォームの初期化
    form = SearchForm(request.GET or None)

    # リセット処理
    if request.GET.get('reset') == 'true':
        results = Product.objects.all()
        paginator = Paginator(results, 9)
        page_number = 1  # リセット後は1ページ目
        page_obj = paginator.get_page(page_number)

        return render(request, 'search.html', {
            'form': SearchForm(),  # 空のフォームを渡す
            'page_obj': page_obj,
            'query': '',
            'category_name': '',
            'min_price': '',
            'max_price': '',
            'sort_by': '',
            'popular_products': get_popular_products(),
        })

    # クエリセットの初期化（すべてのProductを取得）
    results = Product.objects.all()

    # URLパラメータから検索条件を取得
    query = request.GET.get('query', '').strip()
    category_name = request.GET.get('category', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    sort_by = request.GET.get('sort', 'name')

    # フィルタリング処理
    if query:
        results = results.filter(name__icontains=query)

    if category_name:
        try:
            category = Category.objects.get(name=category_name)
            results = results.filter(category_id=category.id)
        except Category.DoesNotExist:
            results = results.none()

    if min_price:
        try:
            results = results.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            results = results.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # 並び替え処理
    if sort_by == 'price_asc':
        results = results.order_by('price')
    elif sort_by == 'price_desc':
        results = results.order_by('-price')
    elif sort_by == 'popularity':
        results = results.annotate(favorites_count=Count('favorite')).order_by('-favorites_count')
    else:
        results = results.order_by('name')

    # ページネーション
    paginator = Paginator(results, 9)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.get_page(1)  # 無効なページ番号の場合は1ページ目を表示

    # テンプレートへのコンテキスト渡し
    context = {
        'form': form,
        'page_obj': page_obj,
        'query': query,
        'category_name': category_name,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'popular_products': get_popular_products(),
    }

    return render(request, 'search.html', context)


def get_popular_products():
    """人気ランキング用のクエリセットを取得"""
    return (
        Product.objects.annotate(favorites_count=Count('favorite'))
        .order_by('-favorites_count')[:3]
    )

@login_required
def mypage_view(request):
    # 現在のビューでは、ユーザー情報を表示する
    # 新たに、購入履歴をデータベースから取得する機能を追加

    # Purchaseモデルからログイン中のユーザーの購入履歴を取得し、
    # 購入日時が新しい順（降順）に並び替え
    purchases = Purchase.objects.filter(user=request.user).order_by('-purchased_at')

    # テンプレートに購入履歴（purchases）を渡して、購入履歴を表示できるようにする
    return render(request, 'mypage.html', {'purchases': purchases})

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
    sort_by = request.GET.get('sort', 'name')

    favorites = Favorite.objects.filter(user=request.user).select_related('product')

    if sort_by == 'price_asc':
        favorites = favorites.order_by('product__price')
    elif sort_by == 'price_desc':
        favorites = favorites.order_by('-product__price')
    elif sort_by == 'popularity':  # 人気順
        favorites = favorites.annotate(favorites_count=Count('product__favorite')).order_by('-favorites_count')
    else:
        favorites = favorites.order_by('product__name')

    return render(request, 'favorites_list.html', {'favorites': favorites})

def product_view(request, pk):
    product = get_object_or_404(Product, pk=pk)

    context = {
        'product': product
    }
    return render(request, 'product_detail.html', context)

def add_to_cart(request, product_id):
    if request.method == 'POST':
        # 商品を取得
        product = get_object_or_404(Product, pk=product_id)
        
        # セッションにカートがない場合は作成
        cart = request.session.get('cart', {})
        
        # カートに商品を追加（数量を1増やす）
        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += 1
        else:
            cart[str(product_id)] = {
                'name': product.name,
                'price': float(product.price),  # Decimalをfloatに変換
                'quantity': 1,
            }
        
        # セッションにカートを保存
        request.session['cart'] = cart
        
        # メッセージを表示
        messages.success(request, f"{product.name}をカートに追加しました。")
        
        # JSONレスポンスを返す
        return JsonResponse({
            'message': f"{product.name}をカートに追加しました。",
            'cart_count': sum(item['quantity'] for item in cart.values())
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
    
def cart_view(request):
    cart = request.session.get('cart', {})  # セッションからカートを取得
    total_price = 0  # 合計金額を初期化
    cart_items = []  # 商品情報を格納するリスト

    # カート内の各商品について処理
    for product_id, product_data in cart.items():
        subtotal = product_data['price'] * product_data['quantity']  # 小計を計算
        product_data['subtotal'] = subtotal  # 小計を商品データに追加
        product_data['product_id'] = product_id  # product_idを商品データに追加
        cart_items.append(product_data)  # 商品情報をリストに追加
        total_price += subtotal  # 合計金額に小計を加算

    # コンテキストにカート情報と合計金額を追加
    context = {
        'cart_items': cart_items,  # 計算済みのカートアイテム
        'total_price': total_price,  # 合計金額
    }
    return render(request, 'cart.html', context)

def remove_from_cart(request, product_id):
    if request.method == 'POST':
        # カートから商品を削除
        cart = request.session.get('cart', {})

        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart

        # カート画面にリダイレクト
        return redirect('cart')  # 'cart_view'はカートの表示ページのURL名

def update_quantity(request, product_id):
    if request.method == 'POST':
        # セッションからカートを取得
        cart = request.session.get('cart', {})

        # 商品がカートに存在するかチェック
        if str(product_id) in cart:
            try:
                # フォームから数量を取得（空の場合は1）
                quantity = int(request.POST.get('quantity', 1))
                
                # 数量が1未満の場合は1に設定
                if quantity < 1:
                    quantity = 1
                
                # カート内の商品数量を更新
                cart[str(product_id)]['quantity'] = quantity
                
                # セッションに更新したカートを保存
                request.session['cart'] = cart
                
                # 成功メッセージ
                messages.success(request, f"{cart[str(product_id)]['name']}の数量を変更しました。")
            except ValueError:
                # 数量が整数でない場合のエラーハンドリング
                messages.error(request, "無効な数量が入力されました。")
        else:
            # 商品がカートにない場合のエラーメッセージ
            messages.error(request, "カートにその商品はありません。")
        
        # カートページにリダイレクト
        return redirect('cart')
    
    # POST以外のリクエストに対する処理
    return redirect('cart')
    
@login_required
def checkout(request):
    # カート情報を取得
    cart = request.session.get('cart', {})
    
    if request.method == 'POST':
        # 購入処理を実行（例: 購入情報をデータベースに保存）
        for product_id, item in cart.items():
            Purchase.objects.create(
                user=request.user,
                product_name=item['name'],  # 商品名
                quantity=item['quantity'],  # 数量
                total_price=item['price'] * item['quantity'],  # 小計（価格 * 数量）
            )
        
        # カートをクリア
        request.session['cart'] = {}

        # 購入完了画面へリダイレクト
        return redirect('purchase_complete')
    
    # GETリクエスト: 購入確認画面を表示
    cart_items = []  # 小計を計算するためのリスト
    total_price = 0
    
    # 小計を計算
    for product_id, item in cart.items():
        item_subtotal = item['price'] * item['quantity']
        cart_items.append({
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'subtotal': item_subtotal,  # 小計を追加
        })
        total_price += item_subtotal  # 合計金額の計算
    
    context = {
        'cart_items': cart_items,  # 小計を含むカートの内容
        'total_price': total_price,  # 合計金額
    }
    
    return render(request, 'checkout.html', context)

@login_required
def purchase_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "カートが空です。")
        return redirect('cart')

    total_price = 0
    for product_id, item in cart.items():
        total_price += item['price'] * item['quantity']
        # 購入履歴に保存
        Purchase.objects.create(
            user=request.user,
            product_name=item['name'],
            quantity=item['quantity'],
            total_price=item['price'] * item['quantity'],
        )
    
    # カートをクリア
    request.session['cart'] = {}

    messages.success(request, "購入が完了しました！")
    # 購入完了画面にリダイレクト
    return redirect('purchase_complete')

@login_required
def purchase_history(request):
    # ユーザーの購入履歴を取得
    purchases = Purchase.objects.filter(user=request.user).order_by('-purchased_at')
    
    # 購入履歴がない場合のフラグを設定
    no_purchases = not purchases.exists()

    # 購入履歴を購入日時ごとにグループ化
    grouped_purchases = defaultdict(list)
    for purchase in purchases:
        # 購入日でグループ化（購入日時を日付部分のみで比較する場合）
        purchase_time = purchase.purchased_at.date()  # 日付部分のみ取得
        grouped_purchases[purchase_time].append(purchase)

    # 購入日時ごとの合計金額を計算
    purchase_totals = {}
    for purchase_time, purchases_in_time in grouped_purchases.items():
        total = sum(purchase.total_price for purchase in purchases_in_time)
        purchase_totals[purchase_time] = total

    context = {
        'purchases': purchases,
        'no_purchases': no_purchases,
        'grouped_purchases': grouped_purchases,
        'purchase_totals': purchase_totals,  # 合計金額をコンテキストに追加
    }

    return render(request, 'purchase_history.html', context)

@login_required
def purchase_complete_view(request):
    return render(request, 'purchase_complete.html')
