# Generated by Django 5.1 on 2024-09-15 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0005_ordermodel_price_delivery'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordermodel',
            name='code',
            field=models.CharField(max_length=200, null=True, unique=True),
        ),
        migrations.AlterModelTable(
            name='ordermodel',
            table=None,
        ),
    ]