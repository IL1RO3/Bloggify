from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User

# Create your models here.


class Category(models.Model):
    title = models.CharField(unique=True, max_length=250)
    def __str__(self):
       return self.title 


class Post(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    title = models.CharField(max_length=200)
    body = models.TextField()
    slug = models.SlugField(unique=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    pub_date = models.DateTimeField(null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True)
    _status = models.CharField(max_length=20, default="draft", choices=STATUS_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:50]
        if self.author and self.author.is_staff:
            self._status = "published"
        super().save(*args, **kwargs)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value.lower() if value else value

    @property
    def active_comments(self):
        return self.comments.filter(active=True)  # type: ignore

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=250)
    email = models.EmailField()
    body = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"comment posted by {self.name} on {self.post.title}"
