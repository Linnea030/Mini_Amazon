from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
#from .forms import RegistrationForm, LoginForm, SearchProductForm
from .models import AmazonUser, Warehouse, Category, Product, Order, Cart
from django.urls import reverse
from django.http import Http404
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib import messages
from django.http import HttpResponse,HttpResponseRedirect
import socket
import math

# function corresponds to urls
from django.contrib.auth.models import User
from django.contrib.auth import login, logout as auth_logout, authenticate
from .forms import UserRegistrationForm, UserEditForm, PurchaseForm, SearchForm
#from .forms import profileForm, userForm, UserProfileUpdateForm, RegisterForm

# Create your views here.

@login_required
def homePage(request):
    return render(request, 'web/home.html')

def registerPage(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid(): 
            username=form.cleaned_data['username']
            # print(username)
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            address = form.cleaned_data['address']

            user = User.objects.create_user(username=username, email=email, password=password2)
            new_user = AmazonUser.objects.create(user=user, phone=phone, address=address, email = email)
            new_user.save()
            return redirect('login')
        else:
            return render(request, 'web/register.html', {'form':form})
    form = UserRegistrationForm()
    return render(request, 'web/register.html', {'form':form})

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request,'Successfully login!')
            return redirect('home')
        else:
            messages.info(request, 'Username or Password is incorrect')
            return redirect('login')

    return render(request, 'web/login.html')

def logoutPage(request):
    auth_logout(request)
    return redirect('login')

def profilePage(request):
    cur_user = request.user
    #is_driver = hasattr(cur_user, 'driverinfo')
    return render(request, 'web/user_profile.html', {'user':cur_user})

@login_required
def user_edit_page(request):
    cur_user = request.user
    if request.method == 'POST':
        form = UserEditForm(request.POST)
        if form.is_valid():
            cur_user.email = form.cleaned_data['email']
            cur_user.amazonuser.phone = form.cleaned_data['phone']
            cur_user.first_name = form.cleaned_data['first_name']
            cur_user.last_name = form.cleaned_data['last_name']
            cur_user.amazonuser.address = form.cleaned_data['address']
            cur_user.save()
            cur_user.amazonuser.save()
            return redirect('user_profile')
        else:
            return render(request, 'web/user_edit.html', {'cur_user':cur_user, 'form':form})
    form = UserEditForm()
    return render(request, 'web/user_edit.html', {'cur_user':cur_user, 'form':form})

def get_closest_wh(address_x, address_y):
    min_dist = float('inf')
    whID = 1
    all_whs = Warehouse.objects.all()
    for wh in all_whs:
        wh_x = wh.x
        wh_y = wh.y
        dist = math.sqrt(math.pow(address_x-wh_x,2)+math.pow(address_y-wh_y,2))
        if dist<min_dist:
            min_dist = dist
            whID = wh.whid
    return whID

@login_required
def category_page(request):
    cur_user = request.user
    cate = Category.objects.all()
    return render(request, 'web/product.html', {'list':cate})

@login_required
def product_page(request, cate_id):
    products = Product.objects.filter(category_id = cate_id).all()
    return render(request, 'web/productD.html', {'list':products})

@login_required
def buy_page(request, product_id):
    user = request.user
    if request.method =='POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            address_x = form.cleaned_data["address_x"]
            address_y = form.cleaned_data["address_y"]
            product_num = form.cleaned_data["productNum"]
            whID = get_closest_wh(address_x, address_y)
            wh = Warehouse.objects.filter(whid=whID).first()
            product = Product.objects.filter(id = product_id).first()

            order = Order(customer = user,product = product, warehouse = wh, address_x = address_x, 
                address_y = address_y, ups_username = user.email, count = product_num)
            order.save()

            subject = "Your order has been placed!"
            content = f'You have ordered {product_num} {product.description}\n'
            content += f'Delivering to {wh}\n'
            content += "Best"
            from_email = 'cyx_0525@163.com'
            email_list = [user.email]
            send_mail(subject,
                      content,
                      from_email = 'cyx_0525@163.com', 
                      recipient_list = email_list,
                      fail_silently=True)
            messages.success(request,'You have successfully made an order!')
            return redirect('home')
        else:
            form = PurchaseForm()
            return render(request,'web/buy.html',{'form':form,'product_id':product_id})
    else:
        form = PurchaseForm()
        return render(request,'web/buy.html',{'form':form,'product_id':product_id})
@login_required
def buy_page1(request, product_id):
    user = request.user
    if request.method =='POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            address_x = form.cleaned_data["address_x"]
            address_y = form.cleaned_data["address_y"]
            product_num = form.cleaned_data["productNum"]
            whID = get_closest_wh(address_x, address_y)
            wh = Warehouse.objects.filter(whid=whID).first()
            product = Product.objects.filter(id = product_id).first()

            order = Order(customer = user,product = product, warehouse = wh, address_x = address_x, 
                address_y = address_y, ups_username = user.email, count = product_num)
            order.save()

            subject = "Your order has been placed!"
            content = f'You have ordered {product_num} {product.description}\n'
            content += f'Delivering to {wh}\n'
            content += "Best"
            from_email = 'cyx_0525@163.com'
            email_list = [user.email]
            send_mail(subject,
                      content,
                      from_email = 'cyx_0525@163.com', 
                      recipient_list = email_list,
                      fail_silently=True)
            messages.success(request,'You have successfully made an order!')
            cart= Cart.objects.filter(customer_id=user.id, product_id=product_id).first()
            cart.delete()
            return redirect('home')
        else:
            form = PurchaseForm()
            return render(request,'web/buy.html',{'form':form,'product_id':product_id})
    else:
        form = PurchaseForm()
        return render(request,'web/buy.html',{'form':form,'product_id':product_id})
    
@login_required
def viewOrder(request):
    context = {}
    user = request.user
    orders = Order.objects.filter(customer_id=user.id)
    #orders = list(orders)
    context['list']=orders
    return render(request,'web/viewOrder.html',{'list':orders,'user': user})

#search for Order
def search(request):
    context = {}
    if(request.method == 'POST'):
        form = SearchForm(request.POST)
        if form.is_valid():
            Name = form.cleaned_data['Name']
            Description = form.cleaned_data['Description']
            Category = form.cleaned_data['Category']
            products = Product.objects.filter(name=Name, description = Description, category_id = Category)
            context['list']=products
            return render(request, 'web/productD.html', {'list':products})
    else :
        form = SearchForm()
        return render(request, 'web/search.html', {'form':form})
    
def add_to_cart(request, product_id):
    user = request.user
    # 获取商品对象
    product = Product.objects.filter(id=product_id)
    new_c = Cart.objects.create(customer_id=user.id, product_id=product_id)
    new_c.save()
    messages.success(request,'Successfully add to cart!')
    return redirect('home')

def delete_cart(request, product_id):
    user = request.user
    cart= Cart.objects.filter(customer_id=user.id, product_id=product_id).first()
    cart.delete()
    messages.success(request,'Successfully delete this product!')
    return redirect('home')

def view_cart(request):
    user = request.user
    cart = Cart.objects.filter(customer_id=user.id)
    products = []
    for c in cart:
        product = Product.objects.filter(id = c.product_id).first()
        products.append(product)
    return render(request, 'web/cart.html', {'list': products})