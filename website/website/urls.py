"""los URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from store import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.marketcap_async, name='index'),
    path('index_products/', views.index_products, name='index_products'),
    path('add_brand/', views.add_brand, name='add_brand'),
    path('brands/', views.list_brands, name='brand_list'),
    path('add_category/', views.add_category, name='add_category'),
    path('categories/', views.list_categories, name='category_list'),
    path('delete_brand/<int:pk>/', views.delete_brand, name='delete_brand'),
    path('delete_category/<int:pk>/', views.delete_category, name='delete_category'),
    path('add_product/', views.add_product, name='add_product'),
    path('product_list/', views.product_list, name='product_list'),
    path('product_list_names/', views.product_list_names, name='product_list_names'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('view_product/<int:product_id>/', views.view_product, name='view_product'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('success/', views.success_view, name='success'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('check_cart_count/', views.check_cart_count, name='check_cart_count'),
    path('cart/', views.view_cart, name='view_cart'),
    path('delete_cart_product/<int:id>', views.delete_cart_product, name='delete_cart_product'),
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add_user/', views.add_user, name='add_user'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('edit_cart/', views.edit_cart, name='edit_cart'),
    path('checkout/confirm/', views.checkout_confirm, name='checkout_confirm'),
    path('checkout_complete/', views.checkout_complete, name='checkout_complete'),
    path('carts/', views.get_all_carts, name='get_all_carts'),
    path('cart/<int:cart_id>/', views.view_cart_details, name='view_cart_details'),
    path('pay_with_stripe/', views.pay_with_stripe, name='pay_with_stripe'),
    # Add additional URLs for success and failure views
    path('success/', views.success, name='success'),
    path('failure/', views.failure, name='failure'),
    path('image/<str:image_url>/<int:height>/', views.display_image, name='display_image'),
    path('resize/<str:image_url>/<int:height>/', views.resize_image, name='resize_image'),
    path('calculate_price/', views.calculate_price, name='calculate_price'),
    path('products/csv/', views.download_csv, name='product_csv'),
    path('ask/', views.ask, name='ask'),
    path('accounts/', include('allauth.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('access_backend_request/<str:url>/', views.access_backend_request, name='access_backend_request'),
    path('access_backend/', views.access_backend, name='access_backend'),
    path('realtime/', views.realtime, name='realtime'),
    path('marketcap/', views.marketcap, name='marketcap'),
    path('marketcap_json/', views.marketcap_json, name='marketcap_json'),
    path('marketcap_async/', views.marketcap_async, name='marketcap_async'),
    
    path('create_token/', views.create_token, name='create_token'),
    path('get_count/', views.get_count, name='get_count'),
    path('bundlecheckerview/', views.bundlecheckerview, name='bundlecheckerview'),


    path('admin/', admin.site.urls),

]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
