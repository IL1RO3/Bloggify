from django.test import TestCase
from .models import Post , Category
from django.utils import timezone
from django.contrib.auth import get_user_model
# Create your tests here.

class PostModelTest(TestCase):
    def test_publish_staff_posts(self):
        User = get_user_model()
        author = User.objects.create(
            username = 'adminnnn',
            password='Gircf@3435',
            is_staff=True
        )
        category = Category.objects.create(title='Test Category')
        
        post = Post.objects.create(
            title = 'Test',
            body='loremipsumefehtegvfdbgfbvdsvvdfvfdvdfvf',
            author = author,
            pub_date=timezone.now(),
            category=category,
        )

        self.assertEqual(post._status , 'published')

    def test_publish_user_posts(self):
        User = get_user_model()
        author = User.objects.create(
            username = 'adminnnn',
            password='Gxrcf@3435',
        )
        category = Category.objects.create(title='Test Category')
        
        post = Post.objects.create(
            title = 'Test',
            body='loremipsumefehtegvfdbgfbvdsvvdfvfdvdfvf',
            author = author,
            pub_date=timezone.now(),
            category=category,
        )

        self.assertEqual(post._status , 'draft')


