from typing import Any

from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views import generic
from . models import *
# Create your views here.

class IndexView(generic.ListView):
    context_object_name = 'posts'
    template_name = 'bloggify/index.html'
    def get_queryset(self):
        return Post.objects.order_by('-pub_date')
    

class DetailView(generic.DateDetailView):
    model = Post
    date_field = 'pub_date'      # Tells Django which date field to use
    month_format = '%m'
    slug_field = 'slug'          # Tells Django which field is the slug
    slug_url_kwarg = 'slug'   
    template_name = 'bloggify/detail.html'
    context_object_name = 'post'
    

