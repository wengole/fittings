# Generated by Django 2.2.8 on 2019-12-13 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fittings', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='dogmaattribute',
            constraint=models.UniqueConstraint(fields=('attribute_id', 'type'), name='unique_type_and_attribute_id'),
        ),
        migrations.AddConstraint(
            model_name='dogmaeffect',
            constraint=models.UniqueConstraint(fields=('effect_id', 'type'), name='unique_type_and_effect_id'),
        ),
    ]