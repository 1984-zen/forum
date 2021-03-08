# Generated by Django 2.2 on 2021-03-08 15:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('labelme_ncku', '0005_labels_dictionary_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='input_imgs',
            old_name='img_path',
            new_name='training_folder_name',
        ),
        migrations.AlterField(
            model_name='labels',
            name='input_img',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='labels', to='labelme_ncku.Input_imgs'),
        ),
        migrations.AlterField(
            model_name='labels',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='labels', to=settings.AUTH_USER_MODEL),
        ),
    ]
