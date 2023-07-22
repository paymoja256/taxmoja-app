from django.contrib import admin

from .models import *

class QuickbooksEfrisClientCredentialsAdmin(admin.ModelAdmin):
    list_display = ['id','client_id','authorisation_id', 'company_name','webhook_key', 'client_secret']

admin.site.register(QuickbooksEfrisClientCredentials,QuickbooksEfrisClientCredentialsAdmin)