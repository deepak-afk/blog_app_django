from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, required=True)
    profile_picture = forms.ImageField(required=False)
    address_line_1 = forms.CharField(max_length=100, required=True, help_text='Required.')
    city = forms.CharField(max_length=50, required=True, help_text='Required.')
    state = forms.CharField(max_length=50, required=True, help_text='Required.')
    pincode = forms.CharField(max_length=6, required=True, help_text='Required.')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'user_type', 'address_line_1', 'password1', 'password2')