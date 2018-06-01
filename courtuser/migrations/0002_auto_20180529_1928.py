# Generated by Django 2.0.2 on 2018-05-29 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courtuser', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='courtuser',
            name='isGuest',
            field=models.BooleanField(default=True, help_text='Gastspieler', verbose_name='Gastspieler'),
        ),
        migrations.AlterField(
            model_name='courtuser',
            name='isSpecial',
            field=models.BooleanField(default=False, help_text='Keine Reservierungseinschränkungen prüfen', verbose_name='Sonder Mitglied'),
        ),
    ]
