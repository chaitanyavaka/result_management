# Generated by Django 5.0.3 on 2024-04-04 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0010_alter_student_regulation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='regulation',
            field=models.CharField(default=None, max_length=10, null=True),
        ),
    ]
