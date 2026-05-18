from django.urls import path
from . import views
urlpatterns = [
    path('',views.ListPostView.as_view(),name='posts')
]