# Generated by Django 2.2 on 2021-02-22 10:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('labelme_ncku', '0003_labels_label_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='labels',
            old_name='mask_path',
            new_name='label_pic_path',
        ),
    ]
