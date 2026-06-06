from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views import generic
from . models import *
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from .forms import AddPostForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# class based views including generics

# mapped to /blogs (main page)
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
    
# post detail view: handles slug using sluggify
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
 

class PostUpdateView(LoginRequiredMixin,generic.edit.UpdateView):
    model = Post
    fields = ['title','body','category']
    template_name = 'registration/update_article.html'
    success_url = reverse_lazy('bloggify:index')
    login_url = "/login/"


class PostDeleteView(LoginRequiredMixin,generic.edit.DeleteView):
    model = Post
    template_name = 'registration/delete_article.html'
    login_url = "/login/"
    success_url = reverse_lazy('bloggify:index')

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['post_title'] = self.object.title #type:ignore
        return context


class Dashboard(LoginRequiredMixin ,generic.ListView):
    template_name = 'bloggify/dashboard.html'
    login_url = 'bloggify:login'
    model = Post
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dash_posts"] = Post.objects.filter(author=self.request.user)
        context["post_count"] = context["dash_posts"].count()
        return context
    
        
# function based views

def contact(request):
    return render(request , 'bloggify/contact.html')


def about(request):
    return render(request , 'bloggify/about.html')


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bloggify:login')
    else:
        form = UserCreationForm()
    return render(request , 'registration/signup.html' ,{'form':form})


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect('bloggify:index')  


@login_required
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
