# Generated by Django 5.0.1 on 2024-06-27 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_processeddata'),
    ]

    operations = [
        migrations.AddField(
            model_name='processeddata',
            name='interval',
            field=models.IntegerField(choices=[(0, 'Not Selected'), (1, 'Houly')], default=0),
        ),
    ]
