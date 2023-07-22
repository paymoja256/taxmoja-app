from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import XeroEfrisClientCredentials, XeroEfrisGoodsAdjustment, XeroEfrisGoodsConfiguration

class MitaCredentialsAdmin(admin.ModelAdmin):
    list_display = ['id','authorisation_id', 'company_name','webhook_key', 'client_secret']
    
class GoodsConfigurationAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    
     list_display = ['id','goods_name', 'goods_code','commodity_tax_category', 'unit_price', 'currency', 'measure_unit', 'description']
    

admin.site.register(XeroEfrisClientCredentials, MitaCredentialsAdmin)
admin.site.register(XeroEfrisGoodsConfiguration,GoodsConfigurationAdmin)
admin.site.register(XeroEfrisGoodsAdjustment)
