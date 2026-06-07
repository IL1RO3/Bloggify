from django.db import migrations
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

def create_can_publish_perm(apps,schema_editor):
    post = apps.get_model('bloggify','Post')
    content_type = ContentType.objects.get_for_model(post)

    Permission.objects.get_or_create(
        codename='can_publish',
        name='Can Publish Posts',
        content_type=content_type
    )

def delete_can_publish_perm(apps, schema_editor):
    Post = apps.get_model('bloggify', 'Post')
    content_type = ContentType.objects.get_for_model(Post)
    Permission.objects.filter(
        codename='can_publish',
        content_type=content_type
    ).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('bloggify','0002_alter_comment_post'),
    ]

    operations = [
        migrations.RunPython(create_can_publish_perm ,reverse_code=delete_can_publish_perm)
    ]