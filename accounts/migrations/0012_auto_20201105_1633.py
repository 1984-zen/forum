# Generated by Django 2.2 on 2020-11-05 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20201104_0936'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='isadmin',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='users',
            name='created_at',
            field=models.DateTimeField(default='2020-11-05 16:33:16'),
        ),
    ]
