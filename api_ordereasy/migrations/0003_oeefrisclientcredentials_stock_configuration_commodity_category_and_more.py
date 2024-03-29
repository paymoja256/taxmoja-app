# Generated by Django 4.2.2 on 2023-07-17 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_ordereasy', '0002_oeefrisclientcredentials_active_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='oeefrisclientcredentials',
            name='stock_configuration_commodity_category',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='oeefrisclientcredentials',
            name='stock_configuration_currency',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='oeefrisclientcredentials',
            name='stock_configuration_measure_unit',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='oeefrisclientcredentials',
            name='stock_configuration_unit_price',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
