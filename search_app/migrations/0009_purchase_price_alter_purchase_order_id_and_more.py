# Generated by Django 5.1.3 on 2024-12-02 00:26

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_app', '0008_purchase_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='order_id',
            field=models.CharField(default=uuid.uuid4, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='total_price',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
    ]
