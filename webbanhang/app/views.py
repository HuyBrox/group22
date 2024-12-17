from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import*
from django.http import HttpResponse,JsonResponse
import json 


def home(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer =customer,complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items    
    else:
        items=[]
        order = {'get_cart_total':0,'get_cart_items':0}
        cartItems = order['get_cart_items']
    products = Product.objects.all()
    context= {'products':products,'cartItems':cartItems}
    return render(request,'app/home.html',context)
def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer =customer,complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items=[]
        order = {'get_cart_total':0,'get_cart_items':0}
        cartItems = order['get_cart_items']
    context= {'items':items ,'order':order,'cartItems':cartItems}
    return render(request,'app/cart.html',context)
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer =customer,complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items=[]
        order = {'get_cart_total':0,'get_cart_items':0}
        cartItems = order['get_cart_items']
    context= {'items':items ,'order':order,'cartItems':cartItems}
    
    return render(request,'app/checkout.html',context)
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    if request.user.is_authenticated:
        customer = request.user.customer
        product = Product.objects.get(id=productId)
        order,created = Order.objects.get_or_create(customer =customer,complete=False)
        orderItem,created = OrderItem.objects.get_or_create(order=order,product=product)
        if action == 'add':
            orderItem.quantity+=1
        elif action == 'remove':
            orderItem.quantity-=1
        orderItem.save()
        if orderItem.quantity<=0:
             orderItem.delete()
        return JsonResponse('added',safe=False)
def detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(digital=product.digital).exclude(id=product.id)[:4]
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'app/detail.html', context)
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    if str(product_id) not in cart:
        cart[str(product_id)] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
            'image': product.ImageURL
        }
    else:
        cart[str(product_id)]['quantity'] += 1

    request.session['cart'] = cart
    return redirect('cart')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()
                messages.success(request, "User created successfully")
                return redirect('login')
        else:
            messages.error(request, "Passwords do not match")
    return render(request, 'app/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Chuyển hướng đến trang chủ sau khi đăng nhập thành công
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'app/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')



from django.http import JsonResponse
from django.db.models import Q
from .models import Product
import unicodedata

# Hàm loại bỏ dấu
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def search(request):
    query = request.GET.get('q', '').strip()  # Lấy từ khóa tìm kiếm
    if query:
        query_no_accents = remove_accents(query).lower()  # Loại bỏ dấu và chuyển về chữ thường
        # Lọc sản phẩm
        results = Product.objects.filter(
            Q(name__iregex=rf"(?i){query}") |  # Tìm kiếm trực tiếp
            Q(name__icontains=query_no_accents)  # Tìm kiếm không dấu
        )
    else:
        results = Product.objects.none()

    results_list = [
        {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'image': product.ImageURL
        }
        for product in results
    ]
    return JsonResponse(results_list, safe=False)
