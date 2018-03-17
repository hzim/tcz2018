# Generated by Django 2.0.2 on 2018-03-04 17:25

import courts.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tczhour',
            name='tcz_user',
            field=models.ForeignKey(on_delete=models.SET(courts.models.getSentinelUser), related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]