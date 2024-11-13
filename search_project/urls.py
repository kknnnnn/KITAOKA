from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # 追記
from django.conf.urls.static import static  # 追記

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # accountsアプリのURLを追加
    path('', include('search_app.urls')),  # 'search_app'のurls.pyをインクルード
]

# 開発中にメディアファイルを提供できるようにします
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
