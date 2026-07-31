from django import forms
from .models import Order

INPUT_STYLE = 'form-control'
SELECT_STYLE = 'form-control'


class CheckoutForm(forms.ModelForm):
    coupon_code = forms.CharField(
        required=False,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': INPUT_STYLE,
            'placeholder': 'Have a coupon code? Enter it here',
        })
    )

    class Meta:
        model = Order
        fields = ('full_name', 'phone', 'address_line', 'city', 'postal_code', 'country', 'payment_method')
        widgets = {
            'full_name': forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': 'Your full name'}),
            'phone': forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': '+977 98X-XXXXXXX'}),
            'address_line': forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': 'Street address'}),
            'city': forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': 'City'}),
            'postal_code': forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': 'Postal code (optional)'}),
            'country': forms.TextInput(attrs={'class': INPUT_STYLE, 'placeholder': 'Country'}),
            'payment_method': forms.Select(attrs={'class': SELECT_STYLE}),
        }
