# bloggify/urls.py
from django.urls import path
from . import views

app_name = 'bloggify'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('post/<int:year>/<int:month>/<int:day>/<slug:slug>/',  # ← No slash at beginning
         views.DetailView.as_view(), 
         name='post_detail'),
]