# Generated by Django 2.2 on 2020-12-02 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_auto_20201109_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='created_at',
            field=models.DateTimeField(default='2020-12-02 15:58:22'),
        ),
        migrations.RenameField(
            model_name='users',
            old_name='name',
            new_name='username',
        ),
    ]
