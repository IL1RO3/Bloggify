
from django.db.models.query import QuerySet
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views import generic
from . models import *
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from .forms import AddPostForm
from django.contrib.auth.decorators import login_required
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
    date_field = 'pub_date'      
    month_format = '%m'
    slug_field = 'slug'          
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


class PostUpdateView(generic.edit.UpdateView):
    model = Post
    fields = ['title','body','category']
    template_name = 'registration/update_article.html'
    success_url = reverse_lazy('bloggify:index')

class PostDeleteView(generic.edit.DeleteView):
    model = Post
    template_name = 'registration/delete_article.html'
    success_url = reverse_lazy('bloggify:index')

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['post_title'] = self.object.title #type:ignore
        return context


class Dashboard(generic.ListView):
    model = Post
    template_name = 'bloggify/dashboard.html'
    context_object_name = 'dash_posts'
        

def contact(request):
    return render(request , 'bloggify/contact.html')

def about(request):
    return render(request , 'bloggify/about.html')


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('bloggify:index')  


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bloggify:login')
    else:
        form = UserCreationForm()
    return render(request , 'registration/signup.html' ,{'form':form})


@login_required(login_url='/login')
def post_article_view(request):
    if request.method == 'POST':
        form = AddPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if request.user.is_staff:
                post.status = 'published'
                post.pub_date = timezone.now()

            post.save()
            return redirect('bloggify:index')

    else:
        form = AddPostForm()
    return render(request , 'registration/post_article.html',{'form':form})
