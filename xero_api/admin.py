from django.contrib import admin

from .models import XeroEfrisClientCredentials, XeroEfrisGoodsAdjustment, XeroEfrisGoodsConfiguration

class MitaCredentialsAdmin(admin.ModelAdmin):
    list_display = ['id','authorisation_id', 'company_name','webhook_key', 'client_secret']

admin.site.register(XeroEfrisClientCredentials, MitaCredentialsAdmin)
admin.site.register(XeroEfrisGoodsConfiguration)
admin.site.register(XeroEfrisGoodsAdjustment)
