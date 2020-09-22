# Generated by Django 2.2 on 2020-09-11 03:53

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_auto_20200910_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boards',
            name='updated_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.CreateModel(
            name='Posts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30, unique=True)),
                ('content', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(null=True)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum.Boards')),
            ],
        ),
    ]
