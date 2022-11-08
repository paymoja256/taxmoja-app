from django.db import models
from jsonfield import JSONField
from client_authorization.models import OAuth2ClientCredentials

from efris.models import ClientCredentials, EfrisGoodsAdjustment, EfrisGoodsConfiguration

from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.


class XeroEfrisClientCredentials(ClientCredentials,OAuth2ClientCredentials):
    

    xero_purchase_account = models.CharField(
        max_length=10,
        default="300",
    )
    
    xero_stock_in_contact_account = models.CharField(
        max_length=255,
        default="39efa556-8dda-4c81-83d3-a631e59eb6d3",
    )
    xero_exempt_tax_rate_code = models.CharField(
        max_length=10,
        default="NONE",
    )

    xero_standard_tax_rate_code = models.CharField(
        max_length=10,
        default="OUTPUT",
    )

    class Meta:
        verbose_name = "Client Credentials"
        verbose_name_plural = "Client Credentials"

    def __str__(self):
        return self.company_name


class XeroEfrisGoodsConfiguration(EfrisGoodsConfiguration):

    client_account = models.ForeignKey(
        XeroEfrisClientCredentials, null=True, blank=True, on_delete=models.SET_NULL

    )

    class Meta:
        verbose_name = "Goods Configuration"
        verbose_name_plural = "Goods Configuration"

    def __str__(self):
        return self.goods_name


class XeroEfrisGoodsAdjustment(EfrisGoodsAdjustment):
    XERO_ADJUST_CHOICES = [("ACCPAY", "INCREASE"), ("ACCREC", "DECREASE")]

    good = models.ForeignKey(
        XeroEfrisGoodsConfiguration,  null=True, blank=True,on_delete=models.SET_NULL

    )

    xero_invoice_type = models.CharField(
        max_length=10,
        choices=XERO_ADJUST_CHOICES,
        default="ACCPAY",
    )

    class Meta:
        verbose_name = "Goods Adjustment"
        verbose_name_plural = "Goods Adjustment"

    def __str__(self):
        return self.good.goods_name


@receiver(post_save, sender=XeroEfrisGoodsAdjustment)
def create_efris_goods_adjustment(sender, instance, **kwargs):
    from .services import create_xero_goods_adjustment
    create_xero_goods_adjustment(instance.__dict__)


@receiver(post_save, sender=XeroEfrisGoodsConfiguration)
def create_efris_goods_configuration(sender, instance, **kwargs):
    from .services import create_xero_goods_configuration
    create_xero_goods_configuration(instance.__dict__)
