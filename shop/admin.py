from django.contrib import admin
from .models import Category, Product, Maker, Bucket, BucketElem

# Регистрируем модели
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Maker)
admin.site.register(Bucket)
admin.site.register(BucketElem)