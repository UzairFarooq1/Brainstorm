# Generated by Django 4.2.6 on 2023-11-30 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_remove_order_products_in_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('confirmed', 'Order Confirmed'), ('out_for_delivery', 'Out for Delivery'), ('delivered', 'Delivered')], default='Confirmed', max_length=50),
        ),
    ]
