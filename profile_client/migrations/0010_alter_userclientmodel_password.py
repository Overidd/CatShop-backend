# Generated by Django 5.1 on 2024-09-18 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile_client', '0009_alter_userclientmodel_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userclientmodel',
            name='password',
            field=models.TextField(),
        ),
    ]