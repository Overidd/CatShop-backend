# Generated by Django 5.1 on 2024-09-16 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile_client', '0005_rename_patment_date_userpaymentmethodmodel_payment_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpaymentmethodmodel',
            name='amount',
            field=models.FloatField(null=True),
        ),
    ]
