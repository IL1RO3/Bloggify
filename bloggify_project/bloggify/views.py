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
        queryset = Post.objects.filter(_status__iexact='published').order_by('-pub_date')
        
        # Filter by category if selected
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        return context
    
    
class PostDetailView(generic.DateDetailView):
    model = Post
    date_field = 'pub_date'      # Tells Django which date field to use
    month_format = '%m'
    slug_field = 'slug'          # Tells Django which field is the slug
    slug_url_kwarg = 'slug'   
    template_name = 'bloggify/detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_comments'] = Post.active_comments
        return context
    

class CategoryListView(generic.ListView):
    context_object_name = 'posts'
    template_name = 'bloggify/category.html'
        

def contact(request):
    return render(request , 'bloggify/contact.html')

def about(request):
    return render(request , 'bloggify/about.html')

