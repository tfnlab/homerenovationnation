from django import forms
from django.contrib.auth.models import User
from store.models import User
from store.models import Brand
from store.models import Category
from store.models import Product
from store.models import Cart
from multiupload.fields import MultiFileField
from multiupload.widgets import MultiFileInput


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

class EditProfileForm(forms.ModelForm):
    company_name = forms.CharField(max_length=255, required=False)
    company_phone = forms.CharField(max_length=255, required=False)
    company_email_address = forms.CharField(max_length=255, required=False)
    billing_address_line1 = forms.CharField(max_length=255, required=False)
    billing_address_line2 = forms.CharField(max_length=255, required=False)
    billing_city = forms.CharField(max_length=255, required=False)
    billing_state = forms.CharField(max_length=255, required=False)
    billing_zipcode = forms.CharField(max_length=255, required=False)
    billing_country = forms.CharField(max_length=255, required=False)
    shipping_address_line1 = forms.CharField(max_length=255, required=False)
    shipping_address_line2 = forms.CharField(max_length=255, required=False)
    shipping_city = forms.CharField(max_length=255, required=False)
    shipping_state = forms.CharField(max_length=255, required=False)
    shipping_zipcode = forms.CharField(max_length=255, required=False)
    shipping_country = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'username', 'company_name', 'company_phone', 'company_email_address',
            'billing_address_line1', 'billing_address_line2', 'billing_city', 'billing_state', 'billing_zipcode', 'billing_country',
            'shipping_address_line1', 'shipping_address_line2', 'shipping_city', 'shipping_state', 'shipping_zipcode', 'shipping_country'
        ]

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False


class ProductForm(forms.ModelForm):
    product_image = MultiFileField(min_num=1, max_num=5, max_file_size=1024*1024*5)  # Example limits    
    class Meta:
        model = Product
        fields = ['name', 'display_priority', 'price', 'wholesale_price', 'your_price', 'description', 'product_image', 'quantity', 'category', 'brand']
        widgets = {
            'product_image': forms.ClearableFileInput(attrs={'multiple': True}),
        }
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['brand'].queryset = Brand.objects.all()
        self.fields['category'].queryset = Category.objects.all()

class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = [
            "billing_address_line1",
            "billing_address_line2",
            "billing_city",
            "billing_state",
            "billing_zipcode",
            "billing_country",
            "shipping_address_line1",
            "shipping_address_line2",
            "shipping_city",
            "shipping_state",
            "shipping_zipcode",
            "shipping_country"
        ]
