from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def checkout_view(request):
    return render(request, 'orders/checkout.html')

@login_required
def order_history(request):
    return render(request, 'orders/history.html')