# Generated by Django 2.2 on 2020-12-07 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_auto_20201203_0938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='created_at',
            field=models.DateTimeField(default='2020-12-07 15:01:58'),
        ),
        migrations.AlterField(
            model_name='users',
            name='date_joined',
            field=models.DateTimeField(default='2020-12-07 15:01:58'),
        ),
        migrations.AlterField(
            model_name='users',
            name='last_login',
            field=models.DateTimeField(default='2020-12-07 15:01:58'),
        ),
    ]