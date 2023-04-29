from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
import uuid
# Create your models here.

class AmazonUser(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    phone = models.CharField(verbose_name='phone', max_length=11, null=True, blank=True)
    address = models.CharField(verbose_name='address', max_length=100, null=True, blank=True)
    email = models.CharField(verbose_name='email', max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.user.username

class Warehouse(models.Model):
    whid = models.IntegerField(primary_key=True,default=1)
    x = models.IntegerField(default=10)
    y = models.IntegerField(default=10)

class Category(models.Model):
    category = models.CharField(max_length=20, null = False, blank = False)

    def __str__(self):
        return self.category

class Product(models.Model):
    # product id using default serial int as primary key
    name = models.CharField(max_length=50,default="")
    description = models.CharField(max_length=200, null = False, blank = False)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null = True)
    price = models.FloatField(default = 9.99, null = False, blank = False)
    avg_score = models.FloatField(default=5)
    num_in_stock = models.IntegerField(default=0)

    def __str__(self):
        return f'<Description: {self.description}, Price: {self.price}>'
    
class Order(models.Model):
    customer = models.ForeignKey(User, related_name='packages', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='orders', on_delete=models.SET_NULL, null = True)
    warehouse = models.ForeignKey(Warehouse, related_name='packages', on_delete=models.SET_NULL,null = True)
    address_x = models.IntegerField(default=1)
    address_y = models.IntegerField(default=1)
    pack_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50,default = "processing")
    ups_username = models.CharField(max_length=50,default = "", blank = True)
    count = models.IntegerField(default = 1)
    is_processed = models.BooleanField(default=False)
    is_packed = models.BooleanField(default=False)
    is_loaded = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    generate_time = models.DateTimeField(default=timezone.now)
    truck_id = models.IntegerField(default = -1)
    is_truck_requested = models.BooleanField(default=False)
    is_truck_arrived = models.BooleanField(default=False)
    is_truck_assigned = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.count} {self.product} in {self.package}'
    # processing 
    # processed 
    # packing    
    # packed     
    # loading    
    # loaded     
    # delivering
    # delivered  
    # error  
    
class Cart(models.Model):
    customer = models.ForeignKey(User, related_name='carts', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='carts', on_delete=models.SET_NULL, null = True)