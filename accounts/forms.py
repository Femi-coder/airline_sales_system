from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Booking

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'password1', 'password2'] 

class BookingStatusForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['status']