# Generated by Django 3.2.13 on 2022-05-06 00:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0005_rename_folder_feed_folders'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feed',
            name='users',
        ),
        migrations.AlterUniqueTogether(
            name='feedsubscription',
            unique_together={('feed', 'folder')},
        ),
        migrations.RemoveField(
            model_name='feedsubscription',
            name='user',
        ),
    ]
