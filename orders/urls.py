from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/',                   views.checkout_view,   name='checkout'),
    path('esewa/initiate/<str:order_number>/', views.esewa_initiate, name='esewa_initiate'),
    path('esewa/success/',              views.esewa_success,   name='esewa_success'),
    path('esewa/failure/',              views.esewa_failure,   name='esewa_failure'),
    path('history/',                    views.order_history,   name='history'),
    path('<str:order_number>/',         views.order_detail,    name='detail'),
]
