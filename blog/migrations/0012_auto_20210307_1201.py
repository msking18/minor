# Generated by Django 3.1.6 on 2021-03-07 06:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_auto_20210306_1836'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='liked',
        ),
        migrations.DeleteModel(
            name='Like',
        ),
    ]
