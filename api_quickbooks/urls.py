from django.urls import path, re_path

from . import views

urlpatterns = [
    path(
        "webhook/<int:client_acc_id>",
        views.webhook,
        name="webhook",
    ),
    path(
        "refresh/<int:client_acc_id>",
        views.refresh,
        name="refresh_token",
    ),
    path(
        "revoke/<int:client_acc_id>",
        views.revoke,
        name="revoke_token",
    ),
    path(
        "auth/<int:client_acc_id>",
        views.oauth2,
        name="oauth2_workflow",
    ),
    path(
        "callback/<int:client_acc_id>",
        views.callback,
        name="callback",
    ),

    path(
        "info/<int:client_acc_id>",
        views.company_info,
        name="company_info",
    ),
    path(
        "stock/configuration/bulk/<int:client_acc_id>",
        views.stock_configuration_bulk_webhook,
        name="qb_stock_configuration_bulk_webhook",
    )
]
