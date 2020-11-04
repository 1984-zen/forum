# Generated by Django 2.2 on 2020-11-04 09:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20201104_0936'),
        ('exams', '0006_exam_files_question'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exam_Users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(editable=False)),
                ('updated_at', models.DateTimeField(null=True)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_users', to='exams.Exams')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_users', to='accounts.Users')),
            ],
        ),
    ]