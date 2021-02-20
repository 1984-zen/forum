from django.db import models
from django.utils import timezone, dateformat

class Input_imgs(models.Model):
    img_name = models.CharField(max_length=255)
    img_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.img_name
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_at = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        self.updated_at = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        return super(Input_imgs, self).save(*args, **kwargs)

class Labels(models.Model):
    label_name = models.CharField(max_length=255)
    label_id = models.CharField(max_length=255, null=True)
    mask_path = models.CharField(max_length=255)
    npy_path = models.CharField(max_length=255, null=True)
    input_img = models.ForeignKey(Input_imgs, on_delete=models.CASCADE, related_name= 'labels')
    user = models.ForeignKey('accounts.Users', on_delete=models.CASCADE, related_name='labels')
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.label_name
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_at = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        self.updated_at = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        return super(Labels, self).save(*args, **kwargs)
