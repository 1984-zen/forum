from django.db import models
from django.utils import timezone, dateformat

class Exams(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey('accounts.Users', on_delete=models.CASCADE)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_at = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        self.updated_at = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        return super(Exams, self).save(*args, **kwargs)

class Questions(models.Model):
    question = models.CharField(max_length=255)
    exam = models.ForeignKey(Exams, on_delete=models.CASCADE, related_name= 'questions')
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.question
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_at = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        self.updated_at = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        return super(Questions, self).save(*args, **kwargs)

class Options(models.Model):
    option = models.CharField(max_length=255)
    is_answer = models.BooleanField(default=False)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name = 'options')
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.option
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_at = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        self.updated_at = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        return super(Options, self).save(*args, **kwargs)

class Option_Users(models.Model):
    user = models.ForeignKey('accounts.Users', on_delete=models.CASCADE, related_name = 'option_users')
    option = models.ForeignKey(Options, on_delete=models.CASCADE, related_name = 'option_users')
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name = 'option_users', null = True)
    exam = models.ForeignKey(Exams, on_delete=models.CASCADE, related_name = 'option_users', null = True)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_at = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        self.updated_at = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        return super(Option_Users, self).save(*args, **kwargs)

class Exam_files(models.Model):
    name = models.CharField(max_length=30)
    file_path = models.CharField(max_length=255)
    type = models.CharField(max_length=10, null=True)
    exam = models.ForeignKey(Exams, on_delete=models.CASCADE, related_name='exam_files')
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, null=True, related_name='exam_files')
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_at = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        self.updated_at = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        return super(Exam_files, self).save(*args, **kwargs)

class Exam_Users(models.Model):
    user = models.ForeignKey('accounts.Users', on_delete=models.CASCADE, related_name='exam_users')
    exam = models.ForeignKey(Exams, on_delete=models.CASCADE, related_name='exam_users')
    date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.user
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_at = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        self.updated_at = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        return super(Exam_files, self).save(*args, **kwargs)