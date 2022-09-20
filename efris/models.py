from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.dispatch import receiver
from django.db.models.signals import post_save
from jsonfield import JSONField


class XeroCredentials(models.Model):
    COUNTRY_CHOICES = [("UG", "UG"), ("ZM", "ZM"), ("BN", "BN")]
    company_name = models.CharField(max_length=100)
    tax_pin = models.CharField(max_length=30)
    webhook_key = models.CharField(max_length=100)
    client_id = models.CharField(max_length=100)
    client_secret = models.CharField(max_length=100)
    callback_uri = models.CharField(max_length=150)
    mita_api_header = models.CharField(max_length=150)
    mita_country_code = models.CharField(
        max_length=10,
        choices=COUNTRY_CHOICES,
        default="UG",
    )
    cred_state = JSONField()

    class Meta:
        verbose_name = "Xero Credentials"
        verbose_name_plural = "Xero Credentials"

    def __str__(self):
        return self.company_name


class XeroGoodsConfiguration(models.Model):
    CURRENCY_CHOICES = [("102", "USD"), ("101", "UGX"), ("104", "EUR")]
    XERO_ACCOUNT_CHOICES = [("300", "PURCHASES")]
    XERO_TAX_CHOICES = [("TAX004", "EXEMPT"), ("TAX003", "VAT")]
    EFRIS_TAX_CHOICES = [("39111527", "EXEMPT"), ("53103003", "VAT")]

    client_account = models.ForeignKey(
        XeroCredentials, on_delete=models.CASCADE

    )
    goods_name = models.CharField(max_length=20, help_text='Goods Name')
    goods_code = models.CharField(max_length=20, help_text='Goods Code')
    xero_purchase_account = models.CharField(
        max_length=10,
        choices=XERO_ACCOUNT_CHOICES,
        default="300",
    )
    xero_tax_rate = models.CharField(
        max_length=10,
        choices=XERO_TAX_CHOICES,
        default="TAX004",
    )
    commodity_tax_category = models.CharField(
        max_length=10,
        choices=EFRIS_TAX_CHOICES,
        default="39111527",
    )
    unit_price = models.FloatField(help_text='Unit Price')
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_CHOICES,
        default="101",
    )

    measure_unit = models.CharField(max_length=20, help_text='Measure Unit')
    description = models.TextField(help_text="Description")

    class Meta:
        verbose_name = "Goods Configuration"
        verbose_name_plural = "Goods Configuration"

    def __str__(self):
        return self.goods_name


class XeroGoodsAdjustment(models.Model):
    CURRENCY_CHOICES = [("102", "USD"), ("101", "UGX"), ("104", "EUR")]
    XERO_ADJUST_CHOICES = [("ACCPAY", "INCREASE"), ("ACCREC", "DECREASE")]
    EFRIS_TAX_RATES = [("39111527", "EXEMPT"), ("53103003", "STANDARD")]
    STOCK_IN_TYPE_CHOICES = [("101", "IMPORT"), ("102", "LPO"), ("104", "OPENING STOCK")]
    ADJUST_TYPE_CHOICES = [("", "NONE"), ("101", "EXPIRED"), ("102", "DAMAGED"), ("104", "OTHERS"),
                           ("103", "PERSONAL USES")]
    OPERATION_TYPE_CHOICES = [("101", "INCREASE INVENTORY"), ("102", "DECREASE INVENTORY")]
    XERO_TAX_CHOICES = [("TAX004", "EXEMPT"), ("TAX003", "VAT")]
    XERO_ACCOUNT_CHOICES = [("300", "PURCHASES")]

    client_account = models.ForeignKey(
        XeroCredentials, on_delete=models.CASCADE

    )

    goods_code = models.CharField(max_length=20, help_text='Goods Code')

    xero_invoice_type = models.CharField(
        max_length=10,
        choices=XERO_ADJUST_CHOICES,
        default="ACCPAY",
    )

    xero_tax_rate = models.CharField(
        max_length=10,
        choices=XERO_TAX_CHOICES,
        default="TAX004",
    )

    xero_purchase_account = models.CharField(
        max_length=10,
        choices=XERO_ACCOUNT_CHOICES,
        default="300",
    )

    purchase_price = models.FloatField(help_text='Purchase Price')
    supplier = models.CharField(max_length=20, help_text='Supplier')
    supplier_tin = models.CharField(max_length=20, help_text='Supplier Tin')
    quantity = models.CharField(max_length=20, help_text='Quantity')

    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_CHOICES,
        default="101",
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


@receiver(post_save, sender=XeroGoodsAdjustment)
def create_goods_adjustment(sender, instance, **kwargs):
    from .views import create_xero_goods_adjustment
    create_xero_goods_adjustment(instance.__dict__)


@receiver(post_save, sender=XeroGoodsConfiguration)
def create_goods_configuration(sender, instance, **kwargs):
    from .views import create_xero_goods_configuration
    create_xero_goods_configuration(instance.__dict__)
