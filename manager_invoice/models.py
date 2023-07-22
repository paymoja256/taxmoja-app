from django.db import models
import jsonfield


SENT_STATUS = [
    ("RECEIVED", "RECEIVED"),
    ("SENDING", "SENDING"),
    ("SENT", "SENT"),
    ("ERROR", "ERROR"),
]

ORIGIN_APPS = [
    ("DEAR", "DEAR"),
    ("XERO", "XERO"),
    ("GENERIC", "GENERIC"),
    ("OTHER", "OTHER"),
]

INVOICE_TYPE = [("INVOICE", "INVOICE"), ("CREDIT", "CREDIT")]

COUNTRY_CODES = [("UG", "UGANDA"), ("ZM", "ZAMBIA"), ("BJ", "BENIN")]

UPLOAD_CODES = [("200", "SUCCESS"), ("400", "ERROR")]


class OutgoingInvoice(models.Model):

    #handles invoices coming from different apps like xero

    origin_invoice_id = models.AutoField(
        primary_key=True, help_text="Instance id from app of origin"
    )

    app_of_origin = models.CharField(
        max_length=100,
        choices=ORIGIN_APPS,
        blank=False,
        null=False,
        default="GENERIC",
    )

    origin_request_data = jsonfield.JSONField()
    mita_request_data = jsonfield.JSONField()
    mita_response_data = jsonfield.JSONField()
    country_code = models.CharField(
        max_length=10,
        choices=COUNTRY_CODES,
        blank=True,
        null=True,
        default="UG",
    )
    mita_upload_code = models.CharField(
        max_length=10,
        choices=UPLOAD_CODES,
        blank=True,
        null=True,
        default="400",
    )
    mita_upload_desc = models.CharField(
        max_length=1000, blank=True, null=True, default="NONE"
    )

    issue_date = models.DateField()
    upload_date = models.DateField()
    modified_date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=SENT_STATUS,
        blank=True,
        null=True,
        default="RECEIVED",
    )

    class Meta:
        verbose_name = "Outgoing Invoice"
        verbose_name_plural = "Incoming Invoices"


class Invoice(models.Model):
    invoice_id = models.AutoField(
        primary_key=True, help_text="Instance id from app of origin"
    )




class EfrisInvoice(models.Model):
    pass