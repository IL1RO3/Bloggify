from django.test import TestCase
from .models import Post, Category, Comment
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse

# Create your tests here.


# helper for testing views
def create_post(title, body, username, password, category, is_staff=False):
    User = get_user_model()
    author = User.objects.create(
        username=username, password=password, is_staff=is_staff
    )
    category = Category.objects.create(title=category)
    post = Post.objects.create(
        title=title,
        body=body,
        author=author,
        pub_date=timezone.now(),
        category=category,
    )
    return post


# tests for models


class PostModelTest(TestCase):
    def test_publish_staff_posts(self):
        post = create_post(
            title="Test",
            body="loremipsumefehtegvfdbgfbvdsvvdfvfdvdfvf",
            username="test",
            password="nigagijwdhfjhvfjsdhkjsd@431A",
            category="test category",
            is_staff=True,
        )
        self.assertEqual(post._status, "published")

    def test_publish_user_posts(self):
        post = create_post(
            title="Test",
            body="loremipsumefehtegvfdbgfbvdsvvdfvfdvdfvf",
            username="test",
            password="nigagijwdhfjhvfjsdhkjsd@431A",
            category="test category",
            is_staff=False,
        )
        self.assertEqual(post._status, "draft")


# test for views
class IndexViewTest(TestCase):
    def test_posts_exist(self):
        post = create_post(
            title="Test",
            body="loremipsumefehtegvfdbgfbvdsvvdfvfdvdfvf",
            username="test",
            password="nigagijwdhfjhvfjsdhkjsd@431A",
            category="test category",
            is_staff=True,
        )
        response = self.client.get(reverse("bloggify:index"))
        self.assertContains(response, post.title)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["posts"], [post])

    def test_no_posts_exist(self):
        response = self.client.get(reverse("bloggify:index"))
        self.assertContains(response, "No posts available in this category.")
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["posts"], [])


class DetailViewTest(TestCase):
    def test_post_is_available(self):
        post = create_post(
            title="Test",
            body="loremipsumefehtegvfdbgfbvdsvvdfvfdvdfvf",
            username="test",
            password="nigagijwdhfjhvfjsdhkjsd@431A",
            category="test category",
            is_staff=True,
        )

        post_date = timezone.localtime(post.pub_date)
        response = self.client.get(
            reverse(
                "bloggify:post_detail",
                args=[post_date.year, post_date.month, post_date.day, post.slug],
            )
        )
        self.assertContains(response, post.title)
        self.assertEqual(response.status_code, 200)

    def test_post_is_not_available(self):
        res_args = [2026, 1, 1, "non-existing-slug"]
        response = self.client.get(reverse("bloggify:post_detail", args=res_args))
        self.assertEqual(response.status_code, 404)

    def test_post_no_comment(self):
        post = create_post(
            title="Test",
            body="loremipsumefehtegvfdbgfbvdsvvdfvfdvdfvf",
            username="test",
            password="nigagijwdhfjhvfjsdhkjsd@431A",
            category="test category",
            is_staff=True,
        )
        post_date = timezone.localtime(post.pub_date)
        response = self.client.get(
            reverse(
                "bloggify:post_detail",
                args=[post_date.year, post_date.month, post_date.day, post.slug],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No comments yet. Be the first to comment!")

    def test_post_active_comment(self):
        post = create_post(
            title="Test",
            body="loremipsumefehtegvfdbgfbvdsvvdfvfdvdfvf",
            username="test",
            password="nigagijwdhfjhvfjsdhkjsd@431A",
            category="test category",
            is_staff=True,
        )

        comment = Comment.objects.create(
            post=post,
            name="test_comment",
            email="test_comment@gmail.com",
            body="awsome tests by the engineer",
            active=True,
        )

        post_date = timezone.localtime(post.pub_date)
        response = self.client.get(
            reverse(
                "bloggify:post_detail",
                args=[post_date.year, post_date.month, post_date.day, post.slug],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, post.active_comments[0].id)
        self.assertQuerySetEqual(response.context["post"].active_comments, [comment])

    def test_post_non_active_comment(self):
        post = create_post(
            title="Test",
            body="loremipsumefehtegvfdbgfbvdsvvdfvfdvdfvf",
            username="test",
            password="nigagijwdhfjhvfjsdhkjsd@431A",
            category="test category",
            is_staff=True,
        )

        comment = Comment.objects.create(
            post=post,
            name="test_comment",
            email="test_comment@gmail.com",
            body="awsome tests by the engineer",
            active=False,
        )

        post_date = timezone.localtime(post.pub_date)
        response = self.client.get(
            reverse(
                "bloggify:post_detail",
                args=[post_date.year, post_date.month, post_date.day, post.slug],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No comments yet. Be the first to comment!")


class UpdateViewTest(TestCase):
    def test_article_update_authorized(self):
        post = create_post(
            title="Test",
            body="loremipsumefehtegvfdbgfbvdsvvdfvfdvdfvf",
            username="test",
            password="nagijwdhfjhvfjsdhkjsd@431A",
            category="test_category",
        )

        self.client.force_login(post.author)

        new_category = Category.objects.create(title="Test category updated")

        updated_data = {
            "title": "Test2fggbdbgbdfbgbg",
            "body": "loremipsumefehtegvfdbgfbvdsvvdfvfdvdfvf",
            "category": new_category.id,
        }

        response = self.client.post(
            reverse("bloggify:update_article", args=[post.id]),
            data=updated_data,
        )

        post.refresh_from_db()

        self.assertEqual(post.title, "Test2fggbdbgbdfbgbg")
        self.assertEqual(post.category, new_category)
        self.assertEqual(response.status_code, 302)

    def test_article_update_non_authorized(self):
        post = create_post(
            title="Test",
            body="loremipsumefehtegvfdbgfbvdsvvdfvfdvdfvf",
            username="test",
            password="nagijwdhfjhvfjsdhkjsd@431A",
            category="test_category",
        )

        updated_data = {
            "title": "Test2fggbdbgbdfbgbg",
            "body": "loremipsumefehtegvfdbgfbvdsvvdfvfdvdfvf",
            "category": post.category.id,
        }

        response = self.client.post(
            reverse("bloggify:update_article", args=[post.id]),
            data=updated_data,
        )

        post.refresh_from_db()

        self.assertEqual(post.title, "Test")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
