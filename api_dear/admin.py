from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import DearCredentials, DearEfrisClientCredentials, DearEfrisGoodsAdjustment, DearEfrisGoodsConfiguration

class DearCredentialsAdmin(admin.ModelAdmin):
    list_display = ['id','company_name','dear_account_id', 'dear_app_key']
    
class GoodsConfigurationAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    
     list_display = ['id','goods_name', 'goods_code','commodity_tax_category', 'unit_price', 'currency', 'measure_unit', 'description']
    

admin.site.register(DearEfrisClientCredentials, DearCredentialsAdmin)
admin.site.register(DearEfrisGoodsConfiguration,GoodsConfigurationAdmin)
admin.site.register(DearEfrisGoodsAdjustment)
admin.site.register(DearCredentials)