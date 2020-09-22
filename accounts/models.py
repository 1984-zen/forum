from django.db import models
from django.utils import timezone, dateformat

class Users(models.Model):
    name = models.CharField(max_length=30)
    account = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(default= dateformat.format(timezone.now(), 'Y-m-d H:i:s'))
    updated_at = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.account