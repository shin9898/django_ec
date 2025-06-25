from django.shortcuts import render
from django.views.generic import ListView

from .models import Cart

# Create your views here.
class CartListView(ListView):
    model = Cart
    template_name = 'cart/cart_list.html'
    context_object_name = 'carts'