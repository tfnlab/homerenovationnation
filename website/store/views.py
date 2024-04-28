from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse

from django.http import FileResponse, Http404
from django.http import JsonResponse
from django.http import HttpResponse

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

from django.views.generic.edit import CreateView
from django.views.generic import View


from django.core.paginator import Paginator
from django import template

import os
import csv
import io
from io import BytesIO
import socket
import uuid

import urllib.request
from django.core.files.base import ContentFile

from django.db.models import Q

from django.utils import timezone  # Import Django's timezone module

import json

from .models import Brand
from .models import Category
from .models import Product
from .models import Cart
from .models import CartProduct
from .models import UserManager
from .models import APIData

from .forms import ProductForm
from .forms import BrandForm
from .forms import CategoryForm
from .forms import UserCreationForm
from .forms import EditProfileForm
from .forms import CartForm

import stripe
from PIL import Image
import openai
import requests

from django.views.decorators.csrf import csrf_exempt
from django.template.context_processors import csrf
from lxml import html

register = template.Library()

def ask(request):
    search_key = None
    if request.method == 'GET':
        search_key = request.GET.get('search_query')
    elif request.method == 'POST':
        search_key = request.POST.get('search_query')

    human = "my customer is asking '" + search_key + "' provide my response to customer as json string with response text to customer marked as customerResponse and a 'one word' product recomendation search text marked as searchText"
    #human = "create a multi color pixel art, shape or pattern on 8 by 8 2d plan responde with properly formated json object with property name enclosed in double quotes provide a meaningful image name which tells what you drew as attribute 'imageName' and color for each cell in hexadecimal color code as list 8 rows and 8 columns called 'cells'"
    SECRET_KEY = os.getenv('OPENAI_SECRET_KEY')
    openai.api_key = SECRET_KEY
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt="The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?\nHuman: "+ human +"\nAI:",
      temperature=0.9,
      max_tokens=2000,
      top_p=1,
      frequency_penalty=0.0,
      presence_penalty=0.6,
      stop=[" Human:", " AI:"]
    )

    titles = response.choices[0].text
    print(titles)
    titles_stripped = titles[titles.find('{'):titles.rfind('}')+1]
    print(titles_stripped)


    titles_dict = json.loads(titles_stripped)

    # Extract the imageDescription and caption keys from the resulting dictionary
    story_text = titles_dict["customerResponse"]
    search_text = titles_dict["searchText"]
    print(story_text)
    return render(request, 'ask.html', {'query': story_text, 'search_text': search_text})

def download_csv(request):
    # Get all products from the Product model
    products = Product.objects.all()

    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'

    # Create a CSV writer and write the header row
    writer = csv.writer(response)
    writer.writerow(['ID', 'SKU', 'Name', 'Price', 'Wholesale Price', 'Your Price', 'Source Upload', 'Description', 'Created At', 'Updated At', 'Product Image', 'Quantity', 'Category', 'Brand', 'Wholesale Price Item JSON','Product Image Link'])

    # Write the product data to the CSV
    for product in products:
        writer.writerow([
            product.id,
            product.sku,
            product.name,
            product.price,
            product.wholesale_price,
            product.your_price,
            product.source_upload,
            product.description,
            product.created_at,
            product.updated_at,
            product.product_image,
            product.quantity,
            product.category.name,
            product.brand.name,
            product.wholesale_price_item_json,
            "https://modernfarms.io/media/" + str(product.product_image),
        ])

    return response

def view_product(request, product_id):
    product = Product.objects.get(id=product_id)

    if product.source_upload == 'www.hydrofarm.com' :
        json_data = json.loads(product.wholesale_price_item_json)
        for key, value in json_data.items():
            print(key + ": " )
            print(value)
        wholesale_prices = json_data['wholesalePrice']['wholesalePrice']
        for item in wholesale_prices:
            print(item['yourPrice'])
        context = {'product': product, 'wholesale_prices' : wholesale_prices}
        return render(request, 'view_product.html', context)
    else :
        context = {'product': product, 'wholesale_prices' : '{}'}
        return render(request, 'view_product.html', context)


def generate_id():
    return uuid.uuid4().hex

def index(request):
    #url = "https://client-api-2-74b1891ee9f9.herokuapp.com/coins?offset=0&limit=20&sort=created_timestamp&order=DESC&includeNsfw=true"  # Replace this with the URL you want to call
    #response = requests.get(url, timeout=60)
    #json_data = None 

    #if response.status_code == 200:
    #    json_data = response.json()

    recent_data = APIData.objects.order_by('-timestamp').first()
    if recent_data and (timezone.now() - recent_data.timestamp).total_seconds() < 1:
        # If a recent cached response exists, return it
        json_data = recent_data.data
    else:
        # If not cached or expired, make the API call
        url = "https://client-api-2-74b1891ee9f9.herokuapp.com/coins?offset=0&limit=20&sort=created_timestamp&order=DESC&includeNsfw=true"
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            json_data = response.json()
            # Save the API response to the database with current timezone-aware timestamp
            APIData.objects.create(data=json_data)
        except requests.exceptions.RequestException as e:
            # Handle exceptions here
            json_data = None

    # Return the JSON data 
        

    cart_id = request.COOKIES.get('cartId')
    if cart_id is None:
        cart_id = generate_id()

    search_key = request.GET.get('search_key', '')
    if request.method == 'POST':
        search_key = request.POST.get('search_key', '')

    context = {'cart_id': cart_id, 'request': request, 'search_key': search_key, 'json_data': json_data}
    response = render(request, 'index.html', context)
    response.set_cookie('cartId', cart_id)
    return response

    return render(request, 'index.html', context)


def index_products(request):
    products = Product.objects.all().order_by('-display_priority')
    print(products.count())
    search_key = None
    if request.method == 'GET':
        search_key = request.GET.get('search_key')
    elif request.method == 'POST':
        search_key = request.POST.get('search_key')
    if search_key is not None and search_key.strip() != "":
        print(search_key)
        products = products.filter(Q(name__icontains=search_key) | Q(description__icontains=search_key))
    print(products.count())
    print(search_key)
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    print(page)
    response = render(request, 'index_products.html', {'products': products, 'request': request})
    return response


def add_to_cart(request):
    cart_id = request.COOKIES.get('cartId')
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        if not quantity or quantity == '':
            quantity = 1
        product_id = request.POST.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid product id'})

        if Cart.objects.filter(external_id=cart_id).exists():
            cart = Cart.objects.get(external_id=cart_id)
        else:
            cart = Cart.objects.create(external_id=cart_id)

        CartProduct.objects.create(cart=cart, product=product, quantity = quantity, price = product.price)

        # Set the cart_id in a cookie
        response = JsonResponse({'status': 'success'})
        response.set_cookie('cartId', cart_id)
        return response
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def delete_cart_product(request, id):
    CartProduct.objects.filter(id=id).delete()
    return redirect('view_cart')

def view_cart(request):
    cart_id = request.COOKIES.get('cartId')
    try:
        cart = Cart.objects.get(external_id=cart_id)
    except Cart.DoesNotExist:
        return redirect('index')
    cart_products = CartProduct.objects.filter(cart=cart)
    products = []
    total = 0
    for cart_product in cart_products:
        line_item_total = cart_product.product.price * cart_product.quantity
        total += line_item_total
        products.append({'product': cart_product.product, 'quantity': cart_product.quantity, 'price': cart_product.price, 'line_item_total': line_item_total, 'id': cart_product.id})

    context = {'products': products, 'total': total}
    return render(request, 'view_cart.html', context)

def check_cart_count(request):
    cart_id = request.COOKIES.get('cartId')

    if request.method == 'GET':
        if CartProduct.objects.filter(cart__external_id=cart_id).exists():
            count = CartProduct.objects.filter(cart__external_id=cart_id).count()
            return JsonResponse({'status': 'success', 'count': count})
        else:
            return JsonResponse({'status': 'error', 'message': 'No cart found'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def list_brands(request):
    brands = Brand.objects.all()
    return render(request, 'brand_list.html', {'brands': brands})

def list_categories(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

def product_list(request):
    products = Product.objects.all()
    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    return render(request, 'product_list.html', {'products': products})

def product_list_names(request):
    products = Product.objects.all()
    return render(request, 'product_list_names.html', {'products': products})

def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('edit_product', product_id=product.id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product_form.html', {'form': form})

def edit_product_view(request,product_id):
    product = Product.objects.get(id=product_id)
    context = {'product': product}
    return render(request, 'edit_product_form.html', context)

def delete_brand(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    brand.delete()
    return redirect('brand_list')

def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('category_list')

def add_brand(request):
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('brand_list')
    else:
        form = BrandForm()
    return render(request, 'add_brand.html', {'form': form})

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

def success_view(request):
    return render(request, 'success.html')

def upload_csv(request):
    socket.setdefaulttimeout(600)  # set timeout to 10 minutes
    if request.method == 'POST':
        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            return HttpResponseBadRequest()
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string)

        fieldnames = ["sku", "url", "name", "webdescription", "retailPrice", "wholesalePrice", "yourPrice", "categoryName", "dc", "source", "wholesalePrice_json"]
        reader = csv.DictReader(io_string, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for row in reader:
            try:
                category = Category.objects.get(name=row['categoryName'])
            except Category.DoesNotExist:
                category = Category.objects.create(name=row['categoryName'])
            try:
                brand = Brand.objects.get(name='brand')
            except Brand.DoesNotExist:
                brand = Brand.objects.create(name='brand')

            print(row.keys())
            product = Product()
            try:
                product = Product.objects.get(sku=row['sku'])
            except Product.DoesNotExist:
                product = Product()
            product.sku = row['sku']
            product.name = row['name']
            product.price = row['retailPrice']
            product.wholesale_price = row['wholesalePrice']
            if row['yourPrice'] != '':
                product.your_price = row['yourPrice']

            product.description = row['webdescription']
            product.quantity = 0
            product.source_upload = row['source']
            product.category = category
            product.brand = brand
            product.wholesale_price_item_json = row['wholesalePrice_json']
            product.save()
            image_url = row['url']
            image_name = f"{product.pk}.jpg" # added here to use pk as file name

            try:
                response = urllib.request.urlopen(image_url, timeout=60)
                product.product_image.save(image_name, ContentFile(response.read()), save=True)
            except urllib.error.URLError as e:
                # handle the exception
                product.product_image.save(image_name, ContentFile(b''), save=True)

        return redirect('success')
    return render(request, 'upload.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('view_cart')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Handle form submission
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('edit_profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('/login')

def edit_cart(request):
    id = request.COOKIES.get('cartId')
    cart = Cart.objects.get(external_id=id)
    if request.method == "POST":
        form = CartForm(request.POST, instance=cart)
        if form.is_valid():
            form.save()
            form = CartForm(instance=cart)
            return render(request, "edit_cart.html", {"form": form})
    else:
        if request.user.is_authenticated:
            user = request.user
            cart.user = user
            cart.save()
            cart.billing_address_line1 = user.billing_address_line1
            cart.billing_address_line2 = user.billing_address_line2
            cart.billing_city = user.billing_city
            cart.billing_state = user.billing_state
            cart.billing_zipcode = user.billing_zipcode
            cart.billing_country = user.billing_country
            cart.shipping_address_line1 = user.shipping_address_line1
            cart.shipping_address_line2 = user.shipping_address_line2
            cart.shipping_city = user.shipping_city
            cart.shipping_state = user.shipping_state
            cart.shipping_zipcode = user.shipping_zipcode
            cart.shipping_country = user.shipping_country
            cart.save();
        form = CartForm(instance=cart)
    return render(request, "edit_cart.html", {"form": form})

def add_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.objects = UserManager()
            user.save()
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'add_user.html', {'form': form})

def checkout_confirm(request):
    id = request.COOKIES.get('cartId')
    cart = Cart.objects.get(external_id=id)
    if request.method == "POST":
        cart.checked_out = True
        cart.save()
        response = redirect('checkout_complete')
        return response
    return render(request, "checkout_confirm.html", {"cart": cart})

def checkout_complete(request):
    return render(request, "checkout_complete.html")

def get_all_carts(request):
    carts = Cart.objects.all()
    return render(request, 'carts.html', {'carts': carts})

def view_cart_details(request, cart_id):
    cart = Cart.objects.get(id=cart_id)
    cart_products = CartProduct.objects.filter(cart=cart)
    products = []
    total = 0
    for cart_product in cart_products:
        line_item_total = cart_product.product.price * cart_product.quantity
        total += line_item_total
        products.append({'product': cart_product.product, 'quantity': cart_product.quantity, 'price': cart_product.price, 'line_item_total': line_item_total, 'id': cart_product.id})

    user = cart.user
    context = {'cart': cart, 'products': products, 'total': total, 'user': user}
    return render(request, 'cart_details.html', context)

stripe.api_key = os.environ.get('STRIPE_KEY')

def pay_with_stripe(request):
    cart_id = request.COOKIES.get('cartId')
    try:
        cart = Cart.objects.get(external_id=cart_id)
    except Cart.DoesNotExist:
        return redirect('index')
    cart_products = CartProduct.objects.filter(cart=cart)
    products = []
    total = 0
    for cart_product in cart_products:
        line_item_total = cart_product.product.price * cart_product.quantity
        total += line_item_total
        products.append({'product': cart_product.product, 'quantity': cart_product.quantity, 'price': cart_product.price, 'line_item_total': line_item_total, 'id': cart_product.id})

    total_in_cents = int(total * 100)

    if request.method == 'POST':
        card_id = request.POST.get('stripeToken')
        try:
            charge = stripe.Charge.create(
                amount=total_in_cents,  # Amount in cents
                currency="usd",
                source=card_id,
                description="Example charge"
            )
        except stripe.error.CardError as e:
            # Handle error
            return redirect('failure')

        if charge.paid:
            cart.paid_transaction_id = charge.id
            cart.paid = True
            cart.save()
            response = redirect('success')
            response.delete_cookie("cartId")
            return response
        else:
            return redirect('failure')
    else:
        int(total * 100)
        context = {'products': products, 'total': total, 'total_in_cents': total_in_cents}
        return render(request, 'pay_with_stripe.html', context)

def success(request):
    return render(request, 'success.html')

def failure(request):
    return render(request, 'failure.html')

def resize_image(url, height):
    # Open the image from URL
    response = urllib.request.urlopen(url)
    img = Image.open(BytesIO(response.read()))

    # Get the original aspect ratio
    aspect_ratio = img.width / img.height

    # Calculate the new width based on the aspect ratio and desired height
    width = int(aspect_ratio * height)

    # Resize the image
    img_resized = img.resize((width, height))

    # Save the resized image to a BytesIO object
    buffer = BytesIO()
    img_resized.save(buffer, format='JPEG')

    # Return the URL for the resized image
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()

def display_image(request, image_url, height):
    context = {
        'image_url': image_url,
        'height': height,
    }
    return render(request, 'display_image.html', context)

def calculate_price(request):
    quantity = request.GET.get('quantity')
    product_id = request.GET.get('product_id')

    product = Product.objects.get(id=product_id)
    json_data = json.loads(product.wholesale_price_item_json)
    for key, value in json_data.items():
        print(key + ": " )
        print(value)
    zero_price = 0
    price = 0
    savings = 0;
    wholesale_prices = json_data['wholesalePrice']['wholesalePrice']
    for item in wholesale_prices:
        if zero_price == 0:
            zero_price = item['yourPrice']
        if float(quantity) >= float(item['qtyStart']) :
            price = item['yourPrice']
    # Perform the calculation and determine the price
    savings = float(zero_price) - float(price)
    #print("Savings: " + str(savings)
    actual_price = float(product.price) - float(savings)
    # Replace this placeholder with your actual logic
    #print(actual_price)
    return JsonResponse({'price': actual_price})

def access_backend_request(request, url):
    username = request.user.hrn_company_code
    email = request.user.email  # Get the user's email
    print(username)
    params = request.GET.dict() if request.method == 'GET' else request.POST.dict()
    params['username'] = username
    params['hrnemail'] = email  # Add the email to the params dictionary

    if '?' in url:
        url = f'https://homerenovationnation.com/{url}&'
    else:
        url = f'https://homerenovationnation.com/{url}?'

    url += '&'.join([f'{k}={v}' for k, v in params.items()])
    print(url)
    if request.method == 'POST':
        print("POST method called")
        data = {
            'username': username,
        }

        for key in request.POST.keys():
            if key.startswith('file_'):
                data[key] = request.FILES[key].read()
            else:
                data[key] = request.POST.get(key)

        headers = {}
        response = requests.post(url, data=data, files=request.FILES, headers=headers)
    else:
        response = requests.get(url)

    # Parse the HTML content
    parsed_html = html.fromstring(response.content)

    # Locate the form element in the parsed HTML
    # Find all forms in the parsed HTML
    forms = parsed_html.findall('.//form')

    if forms:
        # Generate a CSRF token for the current user and request
        csrf_token = csrf(request)['csrf_token']

        # Loop through all forms
        for form in forms:
            # Create a new hidden input element with the CSRF token as its value
            csrf_input = html.Element('input')
            csrf_input.set('type', 'hidden')
            csrf_input.set('name', 'csrfmiddlewaretoken')
            csrf_input.set('value', str(csrf_token))

            # Add the CSRF input element to the form
            form.insert(0, csrf_input)

        # Convert the modified HTML back to a string
        modified_content = html.tostring(parsed_html, encoding='utf-8')

        # Return the modified content as the response to the original request
        return HttpResponse(modified_content, content_type=response.headers['content-type'])
    else:
        # If there's no form in the content, return the original content
        return HttpResponse(response.content, content_type=response.headers['content-type'])

def access_backend(request):
    return render(request, 'main_menu.html')
