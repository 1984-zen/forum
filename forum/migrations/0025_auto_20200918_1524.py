# Generated by Django 2.2 on 2020-09-18 07:24

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0024_auto_20200918_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boards',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 18, 7, 24, 51, 504006, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='post_files',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 18, 7, 24, 51, 550885, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='posts',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 18, 7, 24, 51, 550885, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='recommand_files',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 18, 7, 24, 51, 551883, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='recommands',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 18, 7, 24, 51, 551883, tzinfo=utc)),
        ),
    ]
