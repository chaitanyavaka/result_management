# Generated by Django 5.0.3 on 2024-04-20 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0019_remove_attendance_student_attendance_hour_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='student_roll_no',
            field=models.CharField(max_length=50),
        ),
    ]
