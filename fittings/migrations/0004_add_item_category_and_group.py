# Generated by Django 2.2.12 on 2020-05-23 20:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fittings', '0003_remove_type_description_not_null'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('category_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=250)),
                ('published', models.BooleanField(default=True)),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.RemoveField(
            model_name='type',
            name='group_id',
        ),
        migrations.CreateModel(
            name='ItemGroup',
            fields=[
                ('group_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=250)),
                ('published', models.BooleanField(default=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fittings.ItemCategory')),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.AddField(
            model_name='type',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fittings.ItemGroup'),
        ),
    ]
