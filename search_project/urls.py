from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # accountsアプリのURLを追加
    path('', include('search_app.urls')),  # 'search_app'のurls.pyをインクルード
]
