# Generated by Django 2.2 on 2021-02-19 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labelme_ncku', '0002_labels_npy_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='labels',
            name='label_id',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
