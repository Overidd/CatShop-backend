# Generated by Django 5.1 on 2024-09-16 16:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile_client', '0006_alter_userpaymentmethodmodel_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraddressmodel',
            name='user_client',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_address', to='profile_client.userclientmodel'),
        ),
    ]
