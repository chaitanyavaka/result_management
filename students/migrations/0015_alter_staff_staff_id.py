# Generated by Django 5.0.3 on 2024-04-05 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0014_staff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='staff_id',
            field=models.CharField(max_length=10, primary_key=True, serialize=False),
        ),
    ]
