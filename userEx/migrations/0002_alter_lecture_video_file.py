# Generated by Django 5.1.1 on 2024-12-05 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userEx', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lecture',
            name='video_file',
            field=models.CharField(blank=True, default='null', max_length=500, null=True),
        ),
    ]
