# Generated by Django 4.2.2 on 2023-07-12 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_quickbooks', '0003_quickbooksefrisclientcredentials_basic_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quickbooksefrisclientcredentials',
            name='state',
            field=models.CharField(blank=True, default='NONE', max_length=1000, null=True),
        ),
    ]