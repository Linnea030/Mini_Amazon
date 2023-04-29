from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MaxValueValidator, MinValueValidator
from .models import AmazonUser
import re

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=20, error_messages={'max_length':'Length must be within 20', 'required':'username is required'}, 
        widget = forms.TextInput(attrs={'placeholder':'username', 'class':'form-control'}), label='username')

    password1 = forms.CharField(error_messages={'required':'password is required'}, 
        widget = forms.PasswordInput(attrs={'placeholder':'password', 'class':'form-control'}), label='password1')

    password2 = forms.CharField(error_messages={'required':'password is required'}, 
        widget = forms.PasswordInput(attrs={'placeholder':'password', 'class':'form-control'}), label='password2')

    email = forms.EmailField(error_messages={'required':'email is required'}, 
        widget = forms.EmailInput(attrs={'placeholder':'email', 'class':'form-control'}), label='email')

    phone = forms.IntegerField(error_messages={'required':'phone is required'}, 
        widget = forms.NumberInput(attrs={'placeholder':'phone', 'class':'form-control'}), label='phone')
        
    address = forms.CharField(max_length=50, error_messages={'max_length':'Length must be within 50'}, 
        widget = forms.TextInput(attrs={'placeholder':'address', 'class':'form-control'}), label='address', required=False)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'phone', 'address']


class UserEditForm(forms.Form):
    email = forms.EmailField(error_messages={'required':'email is required'}, 
        widget = forms.EmailInput(attrs={'placeholder':'email', 'class':'form-control'}), label='email')
    phone = forms.IntegerField(error_messages={'required':'phone is required'}, 
        widget = forms.NumberInput(attrs={'placeholder':'phone', 'class':'form-control'}), label='phone')
    first_name = forms.CharField(max_length=20, error_messages={'max_length':'Length must be within 20', 'required':'fisrt name is required'}, 
        widget = forms.TextInput(attrs={'placeholder':'first name', 'class':'form-control'}), label='fisrt_name')
    last_name = forms.CharField(max_length=20, error_messages={'max_length':'Length must be within 20', 'required':'last name is required'}, 
        widget = forms.TextInput(attrs={'placeholder':'last name', 'class':'form-control'}), label='last_name')
    address = forms.CharField(max_length=50, error_messages={'max_length':'Length must be within 50'}, 
        widget = forms.TextInput(attrs={'placeholder':'address', 'class':'form-control', }), label='address', required=False)

    class Meta:
        model = User
        fields = ['email', 'phone', 'first_name', 'last_name', 'address']

class PurchaseForm(forms.Form):
    productNum = forms.IntegerField(label='Number of products',required=True,validators=[MinValueValidator(1)])
    address_x = forms.IntegerField(label='Address x',required=True)
    address_y = forms.IntegerField(label='Address y',required=True)
    

class SearchForm(forms.Form):
    Name = forms.CharField(label = 'Name')
    Description = forms.CharField(label = 'Description')
    Category = forms.ChoiceField(label='Category',
            widget= forms.Select(attrs={'placeholder':'Category', 'class':'form-control'}), 
            choices=(("1", "FOOD"),
                    ("2", "STUDY"),
            )
    )