# Generated by Django 4.2.1 on 2023-06-13 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_dear', '0003_alter_dearcredentials_dear_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dearefrisclientcredentials',
            name='dear_buyer_type_field',
            field=models.CharField(default='NONE', max_length=150),
        ),
        migrations.AddField(
            model_name='dearefrisclientcredentials',
            name='dear_default_cashier',
            field=models.CharField(default='NONE', max_length=150),
        ),
        migrations.AddField(
            model_name='dearefrisclientcredentials',
            name='dear_is_export_field',
            field=models.CharField(default='NONE', max_length=150),
        ),
        migrations.AddField(
            model_name='dearefrisclientcredentials',
            name='dear_tax_pin_field',
            field=models.CharField(default='NONE', max_length=150),
        ),
    ]
