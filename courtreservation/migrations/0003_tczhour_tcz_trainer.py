# Generated by Django 2.0.2 on 2018-03-21 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courtreservation', '0002_tczhour_tcz_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='tczhour',
            name='tcz_trainer',
            field=models.BooleanField(default=False),
        ),
    ]