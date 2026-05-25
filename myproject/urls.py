"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from shop import views
from shop.views import register_view, login_view, logout_view, RegisterView, LoginView, LogoutView, MeView, OrderListView, GetCSRFToken, settings_page, ChangePasswordView, UpdateAccountSettingsView


urlpatterns = [
    path('', views.home, name='home'),  
    path('admin/', admin.site.urls),
    path('catalog/', views.catalog, name='catalog'),  
    path('cart/', views.cart, name='cart'),
    path('api/cart/add/', views.add_to_cart, name='add_to_cart'),
    path('api/cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('api/cart/update/', views.update_cart, name='update_cart'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('api-auth/', include('rest_framework.urls')),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('settings/', settings_page, name='settings'),
    path('account/', views.account_page, name='account'),
    #path('accounts/login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    #path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    path('api/csrf/', GetCSRFToken.as_view(), name='api-csrf'),
    path('api/register/', RegisterView.as_view(), name='api-register'),
    path('api/login/', LoginView.as_view(), name='api-login'),
    path('api/logout/', LogoutView.as_view(), name='api-logout'),
    path('api/me/', MeView.as_view(), name='api-me'),
    path('api/orders/', OrderListView.as_view(), name='api-orders'),
    path('api/change-password/', ChangePasswordView.as_view(), name='api-change-password'),
    path('api/update-account/', UpdateAccountSettingsView.as_view(), name='api-update-account'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)