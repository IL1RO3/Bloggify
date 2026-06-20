from django import forms
from .models import Post, Comment, User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm


class AddPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body", "category"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["name", "email", "body"]


class ModifiedPasswordResetFrom(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data.get("email")
        User = get_user_model()
        if not User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('No account exists with this email address.')
        return email