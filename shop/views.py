from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import viewsets, generics
from .models import Category, Maker, Product, Bucket, BucketElem
from .serializers import (
    CategorySerializer, 
    MakerSerializer, 
    ProductSerializer, 
    BucketSerializer, 
    BucketElemSerializer
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def cart(request):
    """Страница корзины"""
    # Получаем корзину из сессии
    cart = request.session.get('cart', {})
    
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            item_total = product.price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
        except Product.DoesNotExist:
            pass
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    
    return render(request, 'shop/cart.html', context)

@csrf_exempt
def add_to_cart(request):
    """Добавление в корзину - уменьшаем количество на складе"""
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        
        try:
            product = Product.objects.get(id=int(product_id))
            
            # Проверяем есть ли товар на складе
            if product.amount <= 0:
                return JsonResponse({'success': False, 'error': 'Товара нет в наличии'})
            
            # Уменьшаем количество на складе
            product.amount -= 1
            product.save()
            
            # Добавляем в корзину в сессии
            cart = request.session.get('cart', {})
            cart[product_id] = cart.get(product_id, 0) + 1
            request.session['cart'] = cart
            
            return JsonResponse({
                'success': True, 
                'cart_count': sum(cart.values()),
                'stock': product.amount
            })
            
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Товар не найден'})
    
    return JsonResponse({'success': False})

@csrf_exempt
def remove_from_cart(request):
    """Удаление из корзины - возвращаем товар на склад"""
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        
        cart = request.session.get('cart', {})
        
        if product_id in cart:
            quantity = cart[product_id]
            
            # Возвращаем товар на склад
            try:
                product = Product.objects.get(id=int(product_id))
                product.amount += quantity
                product.save()
            except Product.DoesNotExist:
                pass
            
            # Удаляем из корзины
            del cart[product_id]
            request.session['cart'] = cart
            
            return JsonResponse({'success': True, 'stock': product.amount if 'product' in locals() else 0})
    
    return JsonResponse({'success': False})

@csrf_exempt
def update_cart(request):
    """Обновление количества в корзине"""
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        new_quantity = int(data.get('quantity', 1))
        
        cart = request.session.get('cart', {})
        old_quantity = cart.get(product_id, 0)
        
        try:
            product = Product.objects.get(id=int(product_id))
            
            # Разница в количестве
            diff = old_quantity - new_quantity
            
            # Обновляем склад
            product.amount += diff
            product.save()
            
            # Обновляем корзину
            if new_quantity > 0:
                cart[product_id] = new_quantity
            else:
                cart.pop(product_id, None)
            
            request.session['cart'] = cart
            
            return JsonResponse({'success': True, 'stock': product.amount})
            
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Товар не найден'})
    
    return JsonResponse({'success': False})

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        # Вот эта строка добавит ссылку на регистрацию в список:
        'register': reverse('register', request=request, format=format),
        
        # Остальные ссылки из вашего роутера (перечислите нужные):
        'products': reverse('product-list', request=request, format=format),
        'categories': reverse('category-list', request=request, format=format),
        'makers': reverse('maker-list', request=request, format=format),
        'buckets': reverse('bucket-list', request=request, format=format),
    })


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    # Разрешаем доступ всем, чтобы новые люди могли регистрироваться
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MakerViewSet(viewsets.ModelViewSet):
    queryset = Maker.objects.all()
    serializer_class = MakerSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class BucketViewSet(viewsets.ModelViewSet):
    queryset = Bucket.objects.all()
    serializer_class = BucketSerializer

class BucketElemViewSet(viewsets.ModelViewSet):
    queryset = BucketElem.objects.all()
    serializer_class = BucketElemSerializer


def home(request):
    products = Product.objects.all()[:6]  # 6 товаров
    categories = Category.objects.all()
    return render(request, 'shop/index.html', {
        'products': products,
        'categories': categories
    })


def catalog(request):
    products = Product.objects.all()
    

    category_id = request.GET.get('category')
    maker_id = request.GET.get('maker')
    search_query = request.GET.get('search', '')
    
  
    if category_id:
        products = products.filter(category_id=category_id)
    if maker_id:
        products = products.filter(maker_id=maker_id)
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    makers = Maker.objects.all()
    
    context = {
        'products': products_page,
        'categories': categories,
        'makers': makers,
        'selected_category': category_id,
        'selected_maker': maker_id,
        'search_query': search_query,
    }
    
    return render(request, 'shop/catalog.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

