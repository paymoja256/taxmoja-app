from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import  OEEfrisClientCredentials, OEEfrisGoodsAdjustment, OEEfrisGoodsConfiguration

class OECredentialsAdmin(admin.ModelAdmin):
    list_display = ['id','company_name','oe_api_key']
    
class GoodsConfigurationAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    
     list_display = ['id','goods_name', 'goods_code','commodity_tax_category', 'unit_price', 'currency', 'measure_unit', 'description']
    

admin.site.register(OEEfrisClientCredentials, OECredentialsAdmin)
admin.site.register(OEEfrisGoodsConfiguration,GoodsConfigurationAdmin)
admin.site.register(OEEfrisGoodsAdjustment)
