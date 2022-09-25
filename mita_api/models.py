from django.db import models

# Create your models here.


class MitaCredentials(models.Model):

    mita_url = models.CharField(max_length=100)
    active = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mita Credential"
        verbose_name_plural = "Mita Credentials"

    def __str__(self):
        return self.mita_url
