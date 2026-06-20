# bloggify/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import ModifiedPasswordResetFrom

app_name = "bloggify"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path(
        "post/<int:year>/<int:month>/<int:day>/<slug:slug>/",
        views.PostDetailView.as_view(),
        name="post_detail",
    ),
    path("contact/", views.contact_view, name="contact"),
    path("about/", views.about_view, name="about"),
    # auth urls
    path("auth/login/", auth_views.LoginView.as_view(), name="login"),
    path("auth/signup/", views.signup_view, name="signup"),
    path("auth/logout/", views.logout_view, name="logout"),
    path(
        "auth/password_reset",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset.html",
            success_url=reverse_lazy("bloggify:password_reset_done"),
            form_class=ModifiedPasswordResetFrom,
            email_template_name="registration/password_reset_email.html",
        ),
        name="password_reset",
    ),
    path(
        "auth/password_reset/done",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "auth/password_reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url=reverse_lazy("bloggify:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "auth/password_reset/complete",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("post/<int:pk>/edit/", views.PostUpdateView.as_view(), name="update_article"),
    path(
        "post/<int:pk>/delete/", views.PostDeleteView.as_view(), name="delete_article"
    ),
    # dashboard urls
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard/post_article/", views.post_article_view, name="post_article"),
]
