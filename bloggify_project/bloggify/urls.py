# bloggify/urls.py
from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'bloggify'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('post/<int:year>/<int:month>/<int:day>/<slug:slug>/',  # ← No slash at beginning
         views.PostDetailView.as_view(), 
         name='post_detail'),
    path('contact/' , views.contact , name='contact'),
    path('about/' , views.about , name='about'),
    path('login/',auth_views.LoginView.as_view() , name='login'),
    path('logout/',auth_views.LogoutView.as_view() , name='logout'),
    path('signup/', views.signup_view , name='signup')
]