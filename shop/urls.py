from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, MakerViewSet, ProductViewSet, BucketViewSet, BucketElemViewSet, RegisterView
from .views import RegisterView

router = DefaultRouter()
#router.register(r'categories', CategoryViewSet)
#router.register(r'makers', MakerViewSet)
#router.register(r'products', ProductViewSet)
#router.register(r'buckets', BucketViewSet)
#router.register(r'bucket-items', BucketElemViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('api/', include(router.urls)),
    
]