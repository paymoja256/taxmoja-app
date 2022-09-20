from django.urls import path, re_path

from . import views

urlpatterns = [
    path('<int:client_acc_id>/', views.start_xero_auth_view, name='xero_authentication_view'),
    path('callback/<int:client_acc_id>', views.process_callback_view, name='xero_callback_process'),
    path('webhook/<int:client_acc_id>', views.xero_invoice_webhook, name='xero_webhook'),
    path('invoices/<int:client_acc_id>', views.xero_send_invoice_data, name='xero_send_invoice_data'),
    path('contacts/<int:client_acc_id>', views.xero_get_contacts, name='xero_get_contacts'),
    path('items/<int:client_acc_id>', views.xero_get_items, name='xero_get_items'),
    path('items/create/<int:client_acc_id>', views.xero_put_item, name='xero_put_items'),
    path('settings/<int:client_acc_id>', views.test_json_settings, name='test_settings'),
    
]
