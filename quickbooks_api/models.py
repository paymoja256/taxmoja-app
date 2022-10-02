from django.db import models
from client_authorization.models import OAuth2ClientCredentials

from efris.models import ClientCredentials

# Create your models here.

class QuickbooksEfrisClientCredentials(ClientCredentials,OAuth2ClientCredentials):
    
    quick_books_id = models.AutoField(primary_key=True, help_text='quickbooks api auto id')
    


    class Meta:
        verbose_name = " Efris Client Credentials"
        verbose_name_plural = "Efris Client Credentials"

    def __str__(self):
        return self.company_name
    
    
    
class Bearer:
    def __init__(self, refreshExpiry, accessToken, tokenType, refreshToken, accessTokenExpiry, idToken=None):
        self.refreshExpiry = refreshExpiry
        self.accessToken = accessToken
        self.tokenType = tokenType
        self.refreshToken = refreshToken
        self.accessTokenExpiry = accessTokenExpiry
        self.idToken = idToken
