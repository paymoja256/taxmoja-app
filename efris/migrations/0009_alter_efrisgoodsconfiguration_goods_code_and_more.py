# Generated by Django 4.1 on 2022-10-04 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('efris', '0008_alter_efrisgoodsadjustment_supplier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='efrisgoodsconfiguration',
            name='goods_code',
            field=models.CharField(help_text='Goods Code', max_length=200),
        ),
        migrations.AlterField(
            model_name='efrisgoodsconfiguration',
            name='goods_name',
            field=models.CharField(help_text='Goods Name', max_length=200),
        ),
    ]