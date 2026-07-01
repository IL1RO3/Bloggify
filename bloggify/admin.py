from django.contrib import admin
from .models import Category, Comment, Post
from django.utils import timezone

# customize admin panel
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title"]


class PostAdmin(admin.ModelAdmin):
    fields = ["title", "body", "pub_date", "_status", "category", "author"]
    list_filter = ["_status", "pub_date"]
    search_fields = ["title", "body"]
    list_display = ["title", "pub_date", "_status"]
    actions = ["make_publish",'draft_post']

    # action method
    @admin.action(description="Publish Posts")
    def make_publish(self, request, queryset):
        queryset.update(_status="published")
        post_date = timezone.localtime()
        queryset.update(pub_date=post_date)
        
    def draft_post(self , request , queryset):
        queryset.update(_status='draft')
        queryset.update(pub_date=None)




class CommentAdmin(admin.ModelAdmin):
    list_filter = ["active"]
    actions = ["make_active"]

    @admin.action(description="Approve comments")
    def make_active(self, request, queryset):
        queryset.update(active=True)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
