# Generated by Django 5.0.3 on 2024-04-04 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0011_alter_student_regulation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='regulation',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
    ]
