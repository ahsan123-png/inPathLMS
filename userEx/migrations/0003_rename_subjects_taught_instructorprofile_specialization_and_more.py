# Generated by Django 5.1.2 on 2024-11-01 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userEx', '0002_course_discount_end_date_course_discount_percentage_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='instructorprofile',
            old_name='subjects_taught',
            new_name='specialization',
        ),
        migrations.AddField(
            model_name='instructorprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='instructor_profiles/'),
        ),
    ]
