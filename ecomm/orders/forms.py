from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model=Order
        fields = ['first_name', 'last_name', 'phone','email', 'house_no', 'area','landmark', 'country', 'state', 'city', 'pincode', 'order_note']