from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Maker, Product, Bucket, BucketElem, Profile, Order
from django.contrib.auth.models import User
from rest_framework import serializers

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['role', 'full_name', 'phone', 'address', 'delivery_city', 'favorite_category']
        read_only_fields = ['role'] # Менять роль через API пользователю запрещено

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

class OrderSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'username', 'created_at', 'total_amount', 'status']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class MakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maker
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    maker_name = serializers.ReadOnlyField(source='maker.name')
    class Meta:
        model = Product
        fields = ['id', 'name', 'descrip', 'photo', 'price', 'amount', 'category', 'category_name', 'maker', 'maker_name']


class BucketElemSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField(source='cost_elem')
    product_details = ProductSerializer(source='product', read_only=True)
    class Meta:
        model = BucketElem
        fields = ['id', 'bucket', 'product', 'product_details', 'amount', 'total_price']


class BucketSerializer(serializers.ModelSerializer):
    items = BucketElemSerializer(many=True, read_only=True)
    total_cost = serializers.ReadOnlyField(source='cost_value')
    user_username = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Bucket
        fields = ['id', 'user', 'user_username', 'date', 'items', 'total_cost']