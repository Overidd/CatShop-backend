# Generated by Django 5.1 on 2024-09-16 18:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0008_rename_price_orderdetailmodel_price_final_and_more'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='ordermodel',
            table='order',
        ),
    ]