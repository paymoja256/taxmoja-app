from django.contrib import admin

from .models import XeroEfrisClientCredentials, XeroEfrisGoodsAdjustment, XeroEfrisGoodsConfiguration



admin.site.register(XeroEfrisClientCredentials)
admin.site.register(XeroEfrisGoodsConfiguration)
admin.site.register(XeroEfrisGoodsAdjustment)
