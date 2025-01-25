from django.urls import path 
from . import views 
from .views import change_password, toggle_favorite, favorites_list, remove_from_cart
 
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
    path('cart/', views.cart_view, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('update_quantity/<int:product_id>/', views.update_quantity, name='update_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('purchase/', views.purchase_view, name='purchase'),
    path('purchase_history/', views.purchase_history, name='purchase_history'),
    path('purchase_detail/<int:purchase_id>/', views.purchase_detail, name='purchase_detail'),
    path('purchase-complete/', views.purchase_complete_view, name='purchase_complete'),
    path('update_quantity/<int:product_id>/', views.update_quantity, name='update_quantity'),
] 
