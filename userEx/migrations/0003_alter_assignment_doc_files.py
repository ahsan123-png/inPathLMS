# Generated by Django 5.1.1 on 2024-12-05 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userEx', '0002_alter_lecture_video_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='doc_files',
            field=models.URLField(blank=True, null=True),
        ),
    ]
