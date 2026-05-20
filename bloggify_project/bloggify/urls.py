# bloggify/urls.py
from django.urls import path
from . import views

app_name = 'bloggify'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('post/<int:year>/<int:month>/<int:day>/<slug:slug>/',  # ← No slash at beginning
         views.PostDetailView.as_view(), 
         name='post_detail'),
    path('contact/' , views.contact , name='contact'),
    path('about/' , views.about , name='about'),
]