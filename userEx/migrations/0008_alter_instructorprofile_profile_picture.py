# Generated by Django 5.1.1 on 2025-01-06 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userEx', '0007_remove_studentprofile_first_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instructorprofile',
            name='profile_picture',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
