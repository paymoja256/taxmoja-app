from locale import currency
from django.db import models
from django.contrib.postgres.fields import ArrayField

from jsonfield import JSONField


class ClientCredentials(models.Model):
    COUNTRY_CHOICES = [("UG", "UG"), ("ZM", "ZM"), ("BN", "BN")]
    company_name = models.CharField(max_length=100)
    tax_pin = models.CharField(max_length=30)
    mita_api_header = models.CharField(max_length=150)
    mita_country_code = models.CharField(
        max_length=10,
        choices=COUNTRY_CHOICES,
        default="UG",
    )

    class Meta:
        verbose_name = "MiTa Credentials"
        verbose_name_plural = "MiTa Credentials"

    def __str__(self):
        return self.company_name


class EfrisCurrencyCodes(models.Model):

    currency_name = models.CharField(max_length=20, help_text='Currency Name')
    currency_code = models.CharField(max_length=20, help_text='Currency Code')
    currency_abbr = models.CharField(max_length=20, help_text='Currency Abbr')

    def __str__(self):
        return self.currency_name

    class Meta:
        verbose_name = "Efris Currency Code"
        verbose_name_plural = "Efris Currency Codes"

class EfrisMeasureUnits(models.Model):

    measure_unit_name = models.CharField(max_length=20, help_text='Measure Unit Name')
    measure_unit_code = models.CharField(max_length=20, help_text='Measure Unit Code')
    measure_unit_abbr = models.CharField(max_length=20, help_text='Measure Unit Abbr', blank=True,null=True)

    def __str__(self):
        return self.measure_unit_name

    class Meta:
        verbose_name = "Efris Measure Unit"
        verbose_name_plural = "Efris Measure Units"


class EfrisCommodityCategories(models.Model):

    EFRIS_TAX_RATES = [(0.0, "EXEMPT"), (0.18, "STANDARD")]

    efris_commodity_category_name = models.CharField(
        max_length=20, help_text='Efris Commodity Category')
    efris_commodity_category_code = models.CharField(
        max_length=20, help_text='Efris Commodity Category Code')
    tax_rate = models.FloatField(max_length=10,
                                 choices=EFRIS_TAX_RATES,
                                 default=0.18, help_text='Currency Rate')

    def __str__(self):
        return self.efris_commodity_category_name

    class Meta:
        verbose_name = "Efris Commodity Category"
        verbose_name_plural = "Efris Commodity Categories"


class EfrisGoodsConfiguration(models.Model):

    goods_name = models.CharField(max_length=20, help_text='Goods Name')
    goods_code = models.CharField(max_length=20, help_text='Goods Code')

    commodity_tax_category = models.ForeignKey(
        EfrisCommodityCategories, on_delete=models.CASCADE,
        help_text='Efris Commodity Category'

    )
    unit_price = models.FloatField(help_text='Unit Price')
    currency = models.ForeignKey(
        EfrisCurrencyCodes, on_delete=models.CASCADE,
        help_text='Currency'

    )

    measure_unit = models.ForeignKey(
        EfrisMeasureUnits, on_delete=models.CASCADE,
        help_text='Measure Unit'

    )

    description = models.TextField(help_text="Description")

    class Meta:
        verbose_name = " Efris Goods Configuration"
        verbose_name_plural = " Efris Goods Configuration"

    def __str__(self):
        return self.goods_name


class EfrisGoodsAdjustment(models.Model):

    STOCK_IN_TYPE_CHOICES = [
        ("101", "IMPORT"), ("102", "LPO"), ("103", "MANUFACTURING/ASSEMBLY"), ("104", "OPENING STOCK")]
    ADJUST_TYPE_CHOICES = [("", "NONE"), ("101", "EXPIRED"), ("102", "DAMAGED"), ("104", "OTHERS"),
                           ("103", "PERSONAL USES"), ("105", "RAW MATERIALS")]
    OPERATION_TYPE_CHOICES = [
        ("101", "INCREASE INVENTORY"), ("102", "DECREASE INVENTORY")]

    purchase_price = models.FloatField(help_text='Purchase Price')
    supplier = models.CharField(max_length=20, help_text='Supplier')
    supplier_tin = models.CharField(max_length=20, help_text='Supplier Tin')
    quantity = models.CharField(max_length=20, help_text='Quantity')

    currency = models.ForeignKey(
        EfrisCurrencyCodes, on_delete=models.CASCADE

    )

    stock_in_type = models.CharField(
        max_length=10,
        choices=STOCK_IN_TYPE_CHOICES,
        default="101",
    )

    adjust_type = models.CharField(
        max_length=10,
        choices=ADJUST_TYPE_CHOICES,
        default="",
        blank=True, null=True
    )

    operation_type = models.CharField(
        max_length=10,
        choices=OPERATION_TYPE_CHOICES,
        default="",
    )

    purchase_remarks = models.TextField(help_text="Purchase Remarks")

    class Meta:
        verbose_name = "Goods Stock In"
        verbose_name_plural = "Goods Stock In"
