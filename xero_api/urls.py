from django.urls import path, re_path

from . import views

urlpatterns = [
    path('<int:client_acc_id>/', views.start_xero_auth_view,
         name='xero_authentication_view'),
    path('callback/<int:client_acc_id>',
         views.process_callback_view, name='xero_callback_process'),
    path('webhook/<int:client_acc_id>',
         views.xero_invoice_webhook, name='xero_webhook'),



]
