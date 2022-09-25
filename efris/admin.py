from django.contrib import admin


from .models import EfrisCurrencyCodes,EfrisCommodityCategories,EfrisMeasureUnits

class EfrisCurrencyCodesAdmin(admin.ModelAdmin):
    list_display = ['id','currency_name', 'currency_code', 'currency_abbr']
    
class EfrisMeasureUnitAdmin(admin.ModelAdmin):
    list_display = ['id','measure_unit_name', 'measure_unit_code', 'measure_unit_abbr']
    
class EfrisCommodityCategoriesAdmin(admin.ModelAdmin):
    list_display = ['id','efris_commodity_category_name', 'efris_commodity_category_code', 'tax_rate']


admin.site.register(EfrisCurrencyCodes, EfrisCurrencyCodesAdmin)

admin.site.register(EfrisCommodityCategories, EfrisCommodityCategoriesAdmin)


admin.site.register(EfrisMeasureUnits, EfrisMeasureUnitAdmin)
