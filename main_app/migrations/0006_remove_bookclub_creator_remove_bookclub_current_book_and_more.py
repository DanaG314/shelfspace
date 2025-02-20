# Generated by Django 5.1.6 on 2025-02-20 23:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_bookclub_comment_discussion_like'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookclub',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='bookclub',
            name='current_book',
        ),
        migrations.RemoveField(
            model_name='bookclub',
            name='members',
        ),
        migrations.RemoveField(
            model_name='discussion',
            name='book_club',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='book',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='user',
        ),
        migrations.RemoveField(
            model_name='discussion',
            name='user',
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='like',
            name='book',
        ),
        migrations.RemoveField(
            model_name='like',
            name='user',
        ),
        migrations.DeleteModel(
            name='Quote',
        ),
        migrations.DeleteModel(
            name='BookClub',
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
        migrations.DeleteModel(
            name='Discussion',
        ),
        migrations.DeleteModel(
            name='Like',
        ),
    ]
