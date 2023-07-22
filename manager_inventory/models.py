from django.db import models
import jsonfield




class Inventory(models.Model):
    client_id = models.CharField()
    item_code = models.CharField()
    item_name = models.CharField()
    track_item_qty = models.CharField()
    is_purchased = models.CharField()
    cost_price = models.CharField()
    purchase_account = models.CharField()
    purchase_tax_rate = models.CharField()
    is_sold = models.CharField()
    sale_price = models.CharField()
    sale_account = models.CharField()
    sale_tax_rate = models.CharField()
    description = models.CharField()



class EfrisInventory(models.Model):
    item_code = models.CharField()
    client_id = models.CharField()
    mita_request_data = jsonfield.JSONField()
    mita_response_data = jsonfield.JSONField()
  
 





