from django.db import models
from django.utils import timezone, dateformat
from forum.managers import CustomManager

class Boards(models.Model):
    name = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(default= dateformat.format(timezone.now(), 'Y-m-d H:i:s'))
    updated_at = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.name
    
class Posts(models.Model):
    title = models.CharField(max_length=255, unique=True)
    content = models.CharField(max_length=255)
    board = models.ForeignKey(Boards, on_delete=models.CASCADE, related_name='posts')
    user = models.ForeignKey('accounts.Users', on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(default= dateformat.format(timezone.now(), 'Y-m-d H:i:s'))
    updated_at = models.DateTimeField(null=True)
    other = models.CharField(max_length=100, default= "stuff")
    pref = models.CharField(max_length=2, default= "N")
    objects = CustomManager()
    category = models.CharField(max_length=255, default= 'null')
    
    def __str__(self):
        return self.title
    
class Post_files(models.Model):
    name = models.CharField(max_length=30)
    file_path = models.CharField(max_length=255)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='post_files')
    created_at = models.DateTimeField(default= dateformat.format(timezone.now(), 'Y-m-d H:i:s'))
    updated_at = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.name
    
class Recommands(models.Model):
    title = models.CharField(max_length=255)
    content = models.CharField(max_length=255)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='recommands')
    user = models.ForeignKey('accounts.Users', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default= dateformat.format(timezone.now(), 'Y-m-d H:i:s'))
    updated_at = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.title
    
class Recommand_files(models.Model):
    name = models.CharField(max_length=30)
    file_path = models.CharField(max_length=255)
    recommand = models.ForeignKey(Recommands, on_delete=models.CASCADE, related_name='recommand_files', null=True)
    created_at = models.DateTimeField(default= dateformat.format(timezone.now(), 'Y-m-d H:i:s'))
    updated_at = models.DateTimeField(null=True)
    