# Generated by Django 5.1.3 on 2025-01-29 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_app', '0004_point'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='used_points',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
