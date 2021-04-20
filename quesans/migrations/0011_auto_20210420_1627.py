# Generated by Django 3.1.7 on 2021-04-20 10:57

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('quesans', '0010_auto_20210420_1545'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='vote',
        ),
        migrations.AddField(
            model_name='question',
            name='qdownvote',
            field=models.ManyToManyField(related_name='q_downvote', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='question',
            name='qupvote',
            field=models.ManyToManyField(related_name='q_upvote', to=settings.AUTH_USER_MODEL),
        ),
    ]
