def search_view(request):
    form = SearchForm(request.GET or None)
    results = Product.objects.all()  # クエリセットの初期化

    # カテゴリフィルタリング
    category_id = request.GET.get('category')
    if category_id:
        results = results.filter(category__id=category_id)

    # 価格のフィルタリング
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and min_price.isdigit():
        results = results.filter(price__gte=int(min_price))
    if max_price and max_price.isdigit():
        results = results.filter(price__lte=int(max_price))

    # 検索クエリによるフィルタリング
    query = request.GET.get('query')
    if query:
        results = results.filter(name__icontains=query)

    # 並び替え処理
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_asc':
        results = results.order_by('price')
    elif sort_by == 'price_desc':
        results = results.order_by('-price')

    # ページネーション
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # カテゴリ一覧の取得
    categories = Category.objects.all()

    return render(request, 'search.html', {
        'form': form,
        'page_obj': page_obj,
        'categories': categories,  # カテゴリをコンテキストに追加
    })
