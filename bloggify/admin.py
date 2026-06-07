from django.contrib import admin
from .models import Category,Comment,Post

# customize admin panel
class CategoryAdmin(admin.ModelAdmin):
    fields = ['title']
    list_display = ['title']

class PostAdmin(admin.ModelAdmin):
    fields = ['title','body','pub_date','_status','category','author']
    list_filter = ['_status','pub_date']
    search_fields = ["title",'body']
    list_display = ['title','pub_date','_status']
    actions = ['make_publish']

    # action method
    @admin.action(description='Update posts to published.')
    def make_publish(self,request,queryset):
        queryset.update(_status="published")

class CommentAdmin(admin.ModelAdmin):
    list_filter = ['active']
    actions = ['make_active']

    @admin.action(description='Update comments to True')
    def make_active(self,request,queryset):
        queryset.update(active=True)



admin.site.register(Category,CategoryAdmin)
admin.site.register(Post,PostAdmin)
admin.site.register(Comment,CommentAdmin)
