# Generated by Django 2.2 on 2020-09-11 06:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0003_auto_20200911_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posts',
            name='board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='forum.Boards'),
        ),
    ]
