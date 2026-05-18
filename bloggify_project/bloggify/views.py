from typing import Any

from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views import generic
from . models import *
# Create your views here.

class ListCategoryView(generic.ListView):
    context_object_name  = 'categories'
    model = Category
    

class ListPostView(generic.ListView):
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.order_by('-pub_date')
    

class ListcommentView(generic.ListView):
    context_object_name = 'posts'

    def get_queryset(self):
        return Comment.objects.order_by('-pub_date')
