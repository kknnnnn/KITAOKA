# Generated by Django 5.1.3 on 2025-01-25 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_app', '0002_alter_purchase_purchased_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='purchased_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
