# Generated by Django 2.2 on 2020-09-15 06:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0015_auto_20200915_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boards',
            name='created_at',
            field=models.DateTimeField(default='2020-09-15 06:28:27'),
        ),
        migrations.AlterField(
            model_name='post_files',
            name='created_at',
            field=models.DateTimeField(default='2020-09-15 06:28:27'),
        ),
        migrations.AlterField(
            model_name='posts',
            name='created_at',
            field=models.DateTimeField(default='2020-09-15 06:28:27'),
        ),
        migrations.AlterField(
            model_name='recommand_files',
            name='created_at',
            field=models.DateTimeField(default='2020-09-15 06:28:27'),
        ),
        migrations.AlterField(
            model_name='recommand_files',
            name='recommand',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recommand_files', to='forum.Recommands'),
        ),
        migrations.AlterField(
            model_name='recommands',
            name='created_at',
            field=models.DateTimeField(default='2020-09-15 06:28:27'),
        ),
    ]
