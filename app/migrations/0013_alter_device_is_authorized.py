# Generated by Django 5.0.1 on 2024-06-19 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_alter_extenduser_email_alter_extenduser_first_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='is_authorized',
            field=models.IntegerField(choices=[(0, 'Pending'), (1, 'Not Authorized'), (2, 'Authorized')], default=0),
        ),
    ]