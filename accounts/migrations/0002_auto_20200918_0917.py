# Generated by Django 2.2 on 2020-09-18 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='created_at',
            field=models.DateTimeField(default='2020-09-18 01:17:10'),
        ),
    ]
