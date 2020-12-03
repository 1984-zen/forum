from django.db import models
from django.utils import timezone, dateformat
from django.contrib.auth.models import AbstractUser

class Users(AbstractUser):
    account = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=255)
    is_admin = models.IntegerField(default=0)
    created_at = models.DateTimeField(default= dateformat.format(timezone.now(), 'Y-m-d H:i:s'))
    updated_at = models.DateTimeField(null=True)
    date_joined = models.DateTimeField(default= dateformat.format(timezone.now(), 'Y-m-d H:i:s'))
    email = models.CharField(max_length=255, default=0)
    first_name = models.CharField(max_length=30, default=0)
    is_active = models.IntegerField(default=0)
    is_staff = models.IntegerField(default=0)
    is_superuser = models.IntegerField(default=0)
    last_login = models.DateTimeField(default= dateformat.format(timezone.now(), 'Y-m-d H:i:s'))
    last_name = models.CharField(max_length=30, null=True)
    username = models.CharField(max_length=30, unique=True)
    
    def __str__(self):
        return self.account