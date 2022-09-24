from django.db import models

# Create your models here.


class MitaCredentials(models.Model):
    
    mita_url = models.CharField(max_length=100)
    active = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)    
    
    