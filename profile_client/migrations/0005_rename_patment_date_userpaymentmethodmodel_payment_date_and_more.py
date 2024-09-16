# Generated by Django 5.1 on 2024-09-15 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile_client', '0004_remove_userpaymentmethodmodel_user_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userpaymentmethodmodel',
            old_name='patment_date',
            new_name='payment_date',
        ),
        migrations.AddField(
            model_name='userpaymentmethodmodel',
            name='card_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='userpaymentmethodmodel',
            name='card_type',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='userpaymentmethodmodel',
            name='country_code',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='userpaymentmethodmodel',
            name='installments',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='userpaymentmethodmodel',
            name='payment_number',
            field=models.CharField(max_length=100, null=True),
        ),
    ]