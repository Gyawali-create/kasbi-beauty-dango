from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    coupon_code = forms.CharField(required=False, max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Have a coupon code?'}))

    class Meta:
        model = Order
        fields = ('full_name', 'phone', 'address_line', 'city', 'postal_code', 'country', 'payment_method')
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
        }
