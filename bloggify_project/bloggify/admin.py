from django.contrib import admin
from .models import Category,Comment,Post
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    fields = ['title']
    list_display = ['title']

class PostAdmin(admin.ModelAdmin):
    fields = ['title','body','pub_date','_status','category','author']
    

admin.site.register(Category,CategoryAdmin)
admin.site.register(Post,PostAdmin)
admin.site.register(Comment)
