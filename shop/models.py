from django.db import models

from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

def valid_on_sklad(kolvo, x):
    if (kolvo > x):
        raise ValueError


class Category(models.Model):
    name = models.CharField(max_length=100)
    descrip = models.TextField()

    def __str__(self):
        return self.name
    

class Maker(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    descrip = models.TextField()

    def __str__(self):
        return self.name



class Product(models.Model):
    name = models.CharField(max_length=100)
    descrip = models.TextField()
    photo = models.ImageField(upload_to='products/', blank=True, null=True)
    price= models.DecimalField(
        max_digits=10,      
        decimal_places=2,
        validators=[MinValueValidator(0)])
    amount = models.IntegerField(validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    maker = models.ForeignKey(Maker,on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class Bucket(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Владелец корзины",
        related_name="cart"
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Корзина пользователя{self.user.username}"
    
    def cost_value(self):
        total_cost = 0
        try:
            for elem in self.items.all():
                total_cost += elem.cost_elem()
            return total_cost
        except Exception as e:
            print(f"Ошибка подсчета цены товара: {e}")
            return 0

        


class BucketElem(models.Model):
    bucket = models.ForeignKey(Bucket,on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    
    def __str__(self):
        return (f"{self.product.name}, количество - ({self.amount})шт")
    
    def cost_elem(self):
        if (self.amount > self.product.amount):
            raise ValidationError("Введено количество товара больше, чем имеется на складе")
        else:
            return (self.product.price * self.amount)
    
