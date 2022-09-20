from django.contrib import admin

from .models import XeroCredentials, XeroGoodsConfiguration, XeroGoodsAdjustment


class XeroCredentialsAdmin(admin.ModelAdmin):
    list_display = ['tax_pin', 'client_id', 'client_secret', 'webhook_key']


class XeroGoodsConfigurationAdmin(admin.ModelAdmin):
    list_display = ['goods_name', 'goods_code', 'xero_purchase_account', 'xero_tax_rate', 'unit_price', 'currency',
                    'measure_unit', 'commodity_tax_category', 'description']


class XeroGoodsAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['goods_code', 'xero_tax_rate', 'xero_invoice_type', 'purchase_price', 'xero_purchase_account',
                    'stock_in_type', 'currency', 'quantity', 'adjust_type', 'operation_type']


admin.site.register(XeroCredentials, XeroCredentialsAdmin)
admin.site.register(XeroGoodsConfiguration, XeroGoodsConfigurationAdmin)
admin.site.register(XeroGoodsAdjustment, XeroGoodsAdjustmentAdmin)
