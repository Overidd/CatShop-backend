# Generated by Django 5.1 on 2024-09-19 14:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile_client', '0012_userclientmodel_is_staff_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userclientmodel',
            name='is_staff',
        ),
    ]