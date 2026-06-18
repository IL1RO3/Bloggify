# pyright: reportAttributeAccessIssue=false
# above comment is a setting used by Pylance, remove if you are not using it.

from django.test import TestCase
from .models import Post, Category, Comment
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse
from .helpers import create_post

# tests for models


class PostModelTest(TestCase):
    def test_publish_staff_posts(self):
        post = create_post(
            title="Editorial Announcement",
            body="Staff-written posts should be published as soon as they are saved.",
            username="staff_editor",
            password="EditorPass123!",
            category="Announcements",
            is_staff=True,
        )
        self.assertEqual(post._status, "published")

    def test_publish_user_posts(self):
        post = create_post(
            title="Reader Submission",
            body="Regular user posts should stay as drafts until reviewed.",
            username="guest_writer",
            password="WriterPass123!",
            category="Community Stories",
            is_staff=False,
        )
        self.assertEqual(post._status, "draft")


# test for views
class IndexViewTest(TestCase):
    def test_posts_exist(self):
        post = create_post(
            title="Published Django Tips",
            body="A published article should appear on the public index page.",
            username="index_editor",
            password="IndexPass123!",
            category="Django Tips",
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

    def test_index_does_not_show_draft_posts(self):
        draft_post = create_post(
            title="Draft Deployment Checklist",
            body="This draft article should stay hidden from the public index.",
            username="draft_writer",
            password="DraftPass123!",
            category="Private Drafts",
            status="draft",
        )
        published_post = create_post(
            title="Published Release Notes",
            body="This staff article should be visible on the public index.",
            username="release_editor",
            password="ReleasePass123!",
            category="Release Notes",
            is_staff=True,
        )

        response = self.client.get(reverse("bloggify:index"))
        posts = response.context["posts"]
        self.assertContains(response, published_post.title)
        self.assertQuerySetEqual(posts, [published_post])
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, draft_post.title)


class DetailViewTest(TestCase):
    def test_post_is_available(self):
        post = create_post(
            title="Detail Page Walkthrough",
            body="A published post should be available from its dated detail URL.",
            username="detail_editor",
            password="DetailPass123!",
            category="Guides",
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
            title="Quiet Launch Notes",
            body="This article has no comments yet, so the empty message should show.",
            username="quiet_editor",
            password="QuietPass123!",
            category="Launch Notes",
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
            title="Commented Tutorial",
            body="Active comments should be rendered below this tutorial.",
            username="comment_editor",
            password="CommentPass123!",
            category="Tutorials",
            is_staff=True,
        )

        comment = Comment.objects.create(
            post=post,
            name="Helpful Reader",
            email="reader@example.com",
            body="This tutorial helped me understand Django comments.",
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
        self.assertContains(response, comment.body)
        self.assertContains(response, comment.name)
        self.assertQuerySetEqual(response.context["post"].active_comments, [comment])

    def test_post_inactive_comment(self):
        post = create_post(
            title="Moderated Tutorial",
            body="Inactive comments should not be rendered under this article.",
            username="moderator_editor",
            password="ModeratePass123!",
            category="Moderation",
            is_staff=True,
        )

        comment = Comment.objects.create(
            post=post,
            name="Pending Reader",
            email="pending-reader@example.com",
            body="This comment is still waiting for moderation.",
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
        self.assertNotContains(response, comment.body)


class UpdateViewTest(TestCase):

    def test_article_update_authenticated(self):
        post = create_post(
            title="Old Article Title",
            body="The author should be able to update this article.",
            username="article_owner",
            password="OwnerPass123!",
            category="Original Category",
        )

        self.client.force_login(post.author)

        new_category = Category.objects.create(title="Updated Category")

        updated_data = {
            "title": "Updated Article Title",
            "body": "The article body was updated by its original author.",
            "category": new_category.id,
        }

        response = self.client.post(
            reverse("bloggify:update_article", args=[post.id]),
            data=updated_data,
        )

        post.refresh_from_db()

        self.assertEqual(post.title, "Updated Article Title")
        self.assertEqual(post.category, new_category)
        self.assertEqual(response.status_code, 302)

    def test_update_post_unauthenticated(self):
        post = create_post(
            title="Protected Draft",
            body="Anonymous visitors should not be able to update this post.",
            username="protected_owner",
            password="ProtectedPass123!",
            category="Protected Articles",
        )

        updated_data = {
            "title": "Anonymous Update Attempt",
            "body": "This body should not be saved because the user is anonymous.",
            "category": post.category.id,
        }

        response = self.client.post(
            reverse("bloggify:update_article", args=[post.id]),
            data=updated_data,
        )

        post.refresh_from_db()

        self.assertEqual(post.title, "Protected Draft")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_article_update_not_allowed(self):
        post = create_post(
            title="Owner Only Article",
            body="Only the author or staff should be allowed to update this article.",
            username="original_author",
            password="AuthorPass123!",
            category="Owner Articles",
        )

        other_post = create_post(
            title="Different Author Article",
            body="This post exists only to supply a different logged-in author.",
            username="different_author",
            password="DifferentPass123!",
            category="Other Author Articles",
        )

        self.client.force_login(other_post.author)

        updated_data = {
            "title": "Unauthorized Edit Attempt",
            "body": "This body should not be saved by a different author.",
            "category": post.category.id,
        }

        response = self.client.post(
            reverse("bloggify:update_article", args=[post.id]),
            data=updated_data,
        )

        post.refresh_from_db()
        self.assertEqual(post.title, "Owner Only Article")
        self.assertEqual(response.status_code, 403)


class DeleteViewTest(TestCase):
    def test_delete_post_authenticated(self):
        post = create_post(
            title="Article To Delete",
            body="The author should be able to delete this article.",
            username="delete_owner",
            password="DeletePass123!",
            category="Deletion Tests",
        )

        self.client.force_login(post.author)

        response = self.client.post(reverse("bloggify:delete_article", args=[post.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(id=post.id).exists())

    def test_delete_post_unauthenticated(self):
        post = create_post(
            title="Protected Delete Article",
            body="Anonymous visitors should not be able to delete this article.",
            username="protected_delete_owner",
            password="ProtectedDeletePass123!",
            category="Protected Deletes",
        )

        response = self.client.post(reverse("bloggify:delete_article", args=[post.id]))
        post.refresh_from_db()

        self.assertEqual(post.title, "Protected Delete Article")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(id=post.id).exists())

    def test_delete_post_non_author(self):
        post = create_post(
            title="Owner Delete Article",
            body="A different author should not be able to delete this article.",
            username="delete_article_owner",
            password="OwnerDeletePass123!",
            category="Owner Delete Articles",
        )

        other_post = create_post(
            title="Other Author Delete Article",
            body="This post supplies the logged-in non-author for the delete test.",
            username="delete_intruder",
            password="IntruderDeletePass123!",
            category="Other Delete Articles",
        )
        self.client.force_login(other_post.author)
        response = self.client.post(reverse("bloggify:delete_article", args=[post.id]))

        self.assertEqual(post.title, "Owner Delete Article")
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Post.objects.filter(id=post.id).exists())


class DashboardViewTest(TestCase):
    def test_no_post_available(self):
        user = get_user_model()
        user1 = user.objects.create_user(
            username="empty_dashboard_user", password="DashboardPass123!"
        )
        self.client.force_login(user1)
        response = self.client.get(reverse("bloggify:dashboard"))
        self.assertContains(response, "You have no posts yet.")
        self.assertEqual(response.status_code, 200)

    def test_post_exists(self):
        post = create_post(
            title="Dashboard Draft",
            body="The logged-in author should see this post in the dashboard.",
            username="dashboard_owner",
            password="DashboardPass123!",
            category="Dashboard Articles",
        )
        self.client.force_login(post.author)
        response = self.client.get(reverse("bloggify:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, post.title)
        self.assertQuerySetEqual(response.context["dash_posts"], [post])

    def test_not_logged_in_access(self):
        response = self.client.get(reverse("bloggify:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_users_only_see_their_own_post(self):
        my_post = create_post(
            title="My Dashboard Article",
            body="This post belongs to the logged-in dashboard user.",
            username="dashboard_author",
            password="DashboardAuthorPass123!",
            category="My Dashboard Posts",
        )
        other_post = create_post(
            title="Someone Else Dashboard Article",
            body="This post belongs to a different user and should stay hidden.",
            username="other_dashboard_author",
            password="OtherDashboardPass123!",
            category="Other Dashboard Posts",
        )
        self.client.force_login(my_post.author)
        response = self.client.get(reverse("bloggify:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, my_post.title)
        self.assertQuerySetEqual(response.context["dash_posts"], [my_post])
        self.assertNotContains(response, other_post.title)


class StaticViewsTest(TestCase):
    def test_about_view(self):
        response = self.client.get(reverse("bloggify:about"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bloggify/about.html")

    def test_contact_view(self):
        response = self.client.get(reverse("bloggify:contact"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bloggify/contact.html")


class LoginViewTest(TestCase):
    def test_successful_login(self):
        user = get_user_model()
        user.objects.create_user(username="login_user", password="LoginPass123!")
        response = self.client.post(
            reverse("bloggify:login"),
            data={
                "username": "login_user",
                "password": "LoginPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("bloggify:index"))

    def test_unsuccessful_login(self):
        user = get_user_model()
        user.objects.create_user(username="login_user", password="LoginPass123!")
        response = self.client.post(
            reverse("bloggify:login"),
            data={
                "username": "login_user",
                "password": "WrongLoginPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Your username and password didn't match. Please try again."
        )


class LogoutViewTest(TestCase):
    def test_successful_logout(self):
        user = get_user_model()
        user1 = user.objects.create_user(
            username="logout_user", password="LogoutPass123!"
        )
        self.client.force_login(user1)
        response = self.client.post(reverse("bloggify:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("bloggify:index"))

    def test_unauthenticated_logout(self):
        response = self.client.post(reverse("bloggify:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, f'{reverse("bloggify:login")}?next={reverse("bloggify:logout")}'
        )
