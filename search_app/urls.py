from django.urls import path 
from . import views 
from .views import change_password, toggle_favorite, favorites_list
 
urlpatterns = [ 
    path('', views.search_view), 
    path('search/', views.search_view, name='search_view'), 
    path('product/new/', views.product_create, name='product_create'), 
    path('product/<int:pk>/', views.product_detail, name='product_detail'), 
    path('product/<int:pk>/edit/',  views.product_update, name='product_update'), 
    path('product/<int:pk>/delete',  views.product_delete, name='product_delete'), 
    path('product/', views.product_list, name='product_list'), 
    path('mypage/', views.mypage_view, name='mypage'),
    path('change-password/', change_password, name='change_password'),
    path('favorites/<int:product_id>/', toggle_favorite, name='toggle_favorite'),
    path('favorites/', favorites_list, name='favorites_list'),
] 
