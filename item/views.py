from django.shortcuts import render
from django.views.generic.list import ListView

from .models import Item

# Create your views here.
class ItemListView(ListView):
    model = Item
    template_name = 'item_list.html'
