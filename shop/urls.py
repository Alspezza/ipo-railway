from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, MakerViewSet, ProductViewSet, BucketViewSet, BucketElemViewSet, RegisterView
from .views import RegisterView
from .views import register_view, login_view, logout_view
import views

router = DefaultRouter()
#router.register(r'categories', CategoryViewSet)
#router.register(r'makers', MakerViewSet)
#router.register(r'products', ProductViewSet)
#router.register(r'buckets', BucketViewSet)
#router.register(r'bucket-items', BucketElemViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('account/', views.account_page, name='account'),
    path('settings/', views.settings_page, name='settings'),
]