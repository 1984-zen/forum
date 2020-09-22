# Generated by Django 2.2 on 2020-09-18 03:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0019_auto_20200918_1102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boards',
            name='created_at',
            field=models.DateTimeField(default='2020-09-18 03:06:31'),
        ),
        migrations.AlterField(
            model_name='post_files',
            name='created_at',
            field=models.DateTimeField(default='2020-09-18 03:06:31'),
        ),
        migrations.AlterField(
            model_name='posts',
            name='created_at',
            field=models.DateTimeField(default='2020-09-18 03:06:31'),
        ),
        migrations.AlterField(
            model_name='posts',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='accounts.Users'),
        ),
        migrations.AlterField(
            model_name='recommand_files',
            name='created_at',
            field=models.DateTimeField(default='2020-09-18 03:06:31'),
        ),
        migrations.AlterField(
            model_name='recommands',
            name='created_at',
            field=models.DateTimeField(default='2020-09-18 03:06:31'),
        ),
    ]
