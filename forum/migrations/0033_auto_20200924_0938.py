# Generated by Django 2.2 on 2020-09-24 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0032_auto_20200924_0935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boards',
            name='created_at',
            field=models.DateTimeField(default='2020-09-24 09:38:25'),
        ),
        migrations.AlterField(
            model_name='post_files',
            name='created_at',
            field=models.DateTimeField(default='2020-09-24 09:38:25'),
        ),
        migrations.AlterField(
            model_name='posts',
            name='created_at',
            field=models.DateTimeField(default='2020-09-24 09:38:25'),
        ),
        migrations.AlterField(
            model_name='recommand_files',
            name='created_at',
            field=models.DateTimeField(default='2020-09-24 09:38:25'),
        ),
        migrations.AlterField(
            model_name='recommands',
            name='created_at',
            field=models.DateTimeField(default='2020-09-24 09:38:25'),
        ),
    ]
