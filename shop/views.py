from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import viewsets, generics, views, status, permissions
from .models import Category, Maker, Product, Bucket, BucketElem, Profile, Order
from .serializers import (
    CategorySerializer, 
    MakerSerializer, 
    ProductSerializer, 
    BucketSerializer, 
    BucketElemSerializer,
    UserSerializer, 
    ProfileSerializer, 
    OrderSerializer
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

class UpdateAccountSettingsView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        new_username = request.data.get("username")
        new_email = request.data.get("email")

        if not new_username or not new_email:
            return Response({"error": "Поля логин и email не могут быть пустыми"}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем, не занят ли новый логин кем-то другим
        if new_username != user.username and User.objects.filter(username=new_username).exists():
            return Response({"error": "Этот логин уже занят другим пользователем"}, status=status.HTTP_400_BAD_REQUEST)

        user.username = new_username
        user.email = new_email
        user.save()
        
        return Response({
            "success": "Данные успешно обновлены",
            "username": user.username,
            "email": user.email
        })

#Функция, которая просто открывает файл settings.html в браузере
def settings_page(request):
    return render(request, 'shop/settings.html')

class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user.profile, 'role', '') == 'ADMIN'

# Получение CSRF токена для фронтенда
class GetCSRFToken(views.APIView):
    permission_classes = [permissions.AllowAny]
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({'success': 'CSRF cookie set'})

# Регистрация
class RegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role', 'CUSTOMER') # Можно передать ADMIN при создании первого админа

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Пользователь уже существует'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, password=password, email=email)
        user.profile.role = role
        user.profile.full_name = data.get('full_name', '')
        user.profile.save()
        
        return Response({'success': 'Пользователь успешно зарегистрирован'}, status=status.HTTP_201_CREATED)

#Вход 
class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return Response({'success': 'Успешный вход', 'user': UserSerializer(user).data})
        return Response({'error': 'Неверные учетные данные'}, status=status.HTTP_401_UNAUTHORIZED)

#Выход 
class LogoutView(views.APIView):
    def post(self, request):
        logout(request)
        return Response({'success': 'Успешный выход'})

#Эндпоинт /api/me/ (GET и PATCH)
class MeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Эндпоинт /api/orders/ с фильтрацией по ролям
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user.profile, 'role', '') == 'ADMIN':
            return Order.objects.all() # Админ видит всё
        return Order.objects.filter(user=user) # Покупатель — только свои
    
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

def register_view(request):
    if request.user.is_authenticated:
        return redirect('catalog')  
        
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('catalog')
    else:
        form = RegistrationForm()
    return render(request, 'shop/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('catalog')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('catalog')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


class ChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        
        if not user.check_password(old_password):
            return Response({"error": "Неверный старый пароль"}, status=status.HTTP_400_BAD_REQUEST)
            
        user.set_password(new_password)
        user.save()
        login(request, user)  
        return Response({"success": "Пароль изменен"})


def account_page(request):
    return render(request, 'shop/account.html')


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:  # GET доступен всем
            return True
        return request.user and request.user.is_authenticated and getattr(request.user.profile, 'role', '') == 'ADMIN'