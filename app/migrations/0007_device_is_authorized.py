# Generated by Django 5.0.1 on 2024-02-26 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_new'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='is_authorized',
            field=models.BooleanField(default=False),
        ),
    ]