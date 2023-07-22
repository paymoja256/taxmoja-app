from django.urls import path, re_path

from . import views

urlpatterns = [
    path(
        "invoice/<int:client_acc_id>",
        views.invoice_webhook,
        name="oe_invoice_webhook",
    ),
    path(
        "invoice/credit/<int:client_acc_id>",
        views.creditnote_webhook,
        name="oe_credit_webhook",
    ),
    path(
        "stock/configuration/<int:client_acc_id>",
        views.stock_configuration_webhook,
        name="oe_stock_configuration_webhook",
    ),
    path(
        "stock/configuration/bulk/<int:client_acc_id>",
        views.stock_configuration_bulk_webhook,
        name="oe_stock_configuration_bulk_webhook",
    ),
    path(
        "stock/adjustment/<int:client_acc_id>",
        views.stock_adjustment_webhook,
        name="oe_stock_adjustment_webhook",
    ),
]
