# Generated by Django 3.1.6 on 2021-03-22 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_profile_follow_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='face',
            field=models.ImageField(blank=True, upload_to='faces'),
        ),
    ]
