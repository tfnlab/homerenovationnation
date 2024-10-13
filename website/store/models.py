from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import BaseUserManager
import os
import uuid


def default_uuid():
    return str(uuid.uuid4())

class UserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(username=username)
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    company_phone = models.CharField(max_length=255, blank=True)
    company_email_address = models.CharField(max_length=255, blank=True)
    date_joined = models.TimeField(null=True)
    billing_address_line1 = models.CharField(max_length=255, blank=True)
    billing_address_line2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=255, blank=True)
    billing_state = models.CharField(max_length=255, blank=True)
    billing_zipcode = models.CharField(max_length=255, blank=True)
    billing_country = models.CharField(max_length=255, blank=True)
    shipping_address_line1 = models.CharField(max_length=255, blank=True)
    shipping_address_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=255, blank=True)
    shipping_state = models.CharField(max_length=255, blank=True)
    shipping_zipcode = models.CharField(max_length=255, blank=True)
    shipping_country = models.CharField(max_length=255, blank=True)
    hrn_company_code = models.CharField(max_length=255, blank=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    objects = UserManager()

def category_upload_to(instance, filename):
    name, ext = os.path.splitext(filename)
    return f"category/{instance.id}.png"

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=category_upload_to, null=True, blank=True)
    def __str__(self):
        return self.name


def brand_upload_to(instance, filename):
    name, ext = os.path.splitext(filename)
    return f"brand/{instance.id}.png"

class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=brand_upload_to, null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)
    def __str__(self):
        return self.name

def product_upload_to(instance, filename):
    name, ext = os.path.splitext(filename)
    return f"product/{instance.id}.png"

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    sku = models.CharField(max_length=255, default=default_uuid)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    your_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    source_upload = models.TextField(max_length=255, null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    product_image = models.ImageField(upload_to=product_upload_to, null=True, blank=True)
    display_priority = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    wholesale_price_item_json = models.TextField(null=True)
    def __str__(self):
        return self.name

class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    external_id = models.CharField(max_length=255, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    checked_out = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    paid_transaction_id = models.CharField(max_length=255, blank=True)
    billing_address_line1 = models.CharField(max_length=255, blank=True)
    billing_address_line2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=255, blank=True)
    billing_state = models.CharField(max_length=255, blank=True)
    billing_zipcode = models.CharField(max_length=255, blank=True)
    billing_country = models.CharField(max_length=255, blank=True)
    shipping_address_line1 = models.CharField(max_length=255, blank=True)
    shipping_address_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=255, blank=True)
    shipping_state = models.CharField(max_length=255, blank=True)
    shipping_zipcode = models.CharField(max_length=255, blank=True)
    shipping_country = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='carts', null=True, blank=True)
    def __str__(self):
        return self.cart_id

class CartProduct(models.Model):
    id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class APIData(models.Model):
    data = models.JSONField(null=True)  # Store JSON data
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp when the data was saved
    is_retrieving = models.BooleanField(default=False)  # Boolean indicating whether data is being retrieved

    def __str__(self):
        return f"API Data saved at {self.timestamp}"


class Token(models.Model):
    mint = models.CharField(max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    symbol = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image_uri = models.URLField(null=True, blank=True)
    metadata_uri = models.URLField(null=True, blank=True)
    twitter = models.CharField(max_length=300, null=True, blank=True)
    telegram = models.CharField(max_length=100, null=True, blank=True)
    bonding_curve = models.CharField(max_length=100, null=True, blank=True)
    associated_bonding_curve = models.CharField(max_length=100, null=True, blank=True)
    creator = models.CharField(max_length=100, null=True, blank=True)
    created_timestamp = models.DateTimeField(null=True, blank=True)
    raydium_pool = models.CharField(max_length=100, null=True, blank=True)
    complete = models.BooleanField(default=False)
    virtual_sol_reserves = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    virtual_token_reserves = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    hidden = models.BooleanField(default=False)
    total_supply = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    show_name = models.BooleanField(default=False)
    last_trade_timestamp = models.DateTimeField(null=True, blank=True)
    king_of_the_hill_timestamp = models.DateTimeField(null=True, blank=True)
    market_cap = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    reply_count = models.IntegerField(null=True, blank=True)
    last_reply = models.CharField(max_length=100, null=True, blank=True)
    nsfw = models.BooleanField(default=False)
    market_id = models.IntegerField(null=True, blank=True)
    market_id_two = models.IntegerField(null=True, blank=True)
    inverted = models.BooleanField(default=False)
    username = models.CharField(max_length=100, null=True, blank=True)
    profile_image = models.URLField(null=True, blank=True)
    usd_market_cap = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)

    def __str__(self):
        return self.name  # or any other field you want to represent the object with

class Accesstoken(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    access_cookie = models.CharField(max_length=255)
    public_wallet_address = models.CharField(max_length=255, unique=True)
    token_balance = models.FloatField()
    is_scam_filter_on = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.public_wallet_address} - {self.access_cookie}'


class RaidLink(models.Model):
    token_mint = models.CharField(max_length=100)
    url = models.URLField()
    click_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100)

    def __str__(self):
        return f"RaidLink(token_mint={self.token_mint}, url={self.url}, click_count={self.click_count}, created_at={self.created_at}, created_by={self.created_by.username})"


class Tweet(models.Model):
    content = models.TextField()  # The text content of the tweet
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the tweet was created
    is_processed = models.BooleanField(default=False)  # Indicates if the tweet has been processed
    
    def __str__(self):
        return self.content[:50]  # Display the first 50 characters of the tweet

    class Meta:
        ordering = ['-created_at']  # Sort by most recent tweets
