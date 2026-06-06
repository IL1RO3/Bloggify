# bloggify/urls.py
from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'bloggify'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('post/<int:year>/<int:month>/<int:day>/<slug:slug>/', 
         views.PostDetailView.as_view(), 
         name='post_detail'),
    path('contact/' , views.contact , name='contact'),
    path('about/' , views.about , name='about'),
    path('login/',auth_views.LoginView.as_view() , name='login'),
    path('signup/', views.signup_view , name='signup'),
    path('post_article/' , views.post_article_view , name='post_article'),
    path('post/<int:pk>/edit',views.PostUpdateView.as_view(),name='update_article'),
    path('post/<int:pk>/delete',views.PostDeleteView.as_view(),name='delete_article'),
    path('dashboard/' , views.Dashboard.as_view(),name='dashboard'),
    path('dashboard/logout/',auth_views.LogoutView.as_view() , name='logout'),

]