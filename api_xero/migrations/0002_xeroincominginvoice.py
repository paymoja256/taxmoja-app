# Generated by Django 4.2.1 on 2023-06-13 08:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manager_efris', '0002_efrisoutgoinginvoice'),
        ('api_xero', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='XeroIncomingInvoice',
            fields=[
                ('efrisoutgoinginvoice_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='manager_efris.efrisoutgoinginvoice')),
            ],
            bases=('manager_efris.efrisoutgoinginvoice',),
        ),
    ]
