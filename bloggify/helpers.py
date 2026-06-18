from django.contrib.auth import get_user_model
from .models import Category, Post
from django.utils import timezone


# helper for testing views
def create_post(title, body, username, password, category, is_staff=False, status="draft"):
    user = get_user_model()
    author = user.objects.create_user(
        username=username, password=password, is_staff=is_staff
    )
    category = Category.objects.create(title=category)
    post = Post.objects.create(
        title=title,
        body=body,
        author=author,
        pub_date=timezone.now(),
        category=category,
        _status=status,
    )
    return post
