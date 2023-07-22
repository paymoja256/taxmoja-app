from curses.ascii import CR
from django.contrib import admin


from .models import MitaCredentials

class MitaCredentialsAdmin(admin.ModelAdmin):
    list_display = ['id','mita_url', 'active', 'date_created']


admin.site.register(MitaCredentials, MitaCredentialsAdmin)
