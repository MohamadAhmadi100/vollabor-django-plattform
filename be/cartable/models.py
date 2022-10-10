from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here

section_choices = [
    ('Administration section', 'Administration section'),
    ('Research section', 'Research section'),
    ('Industry section', 'Industry section'),
    ('Competition section', 'Competition section'),
    ('Human Resource section', 'Human Resource section'),
    ('Advertisement section', 'Advertisement section'),
    ('Site section', 'Site section'),
    ('Financial section', 'Financial section'),
    ('Workshop section', 'Workshop section')
]


class Letter(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField(max_length=250)
    date = models.DateTimeField(default=timezone.now)
    security = models.CharField(max_length=50)
    number = models.CharField(max_length=100)
    summary = models.TextField(null=False)
    priority = models.CharField(max_length=50)
    attach_file = models.FileField(upload_to='uploads/',null=True)
    document = models.FileField(upload_to='uploads/',null=True)

    def __str__(self):
        # return self.title +" from "+str(self.sender) +" to "#+ str(Receiver.objects.filter(letter=self))
        # return self.title +" from "+str(self.sender) +" to "#+ str(Receiver.objects.filter(letter=self))
        return self.number

    class Meta:
        ordering = ['date']


class Receiver(models.Model):
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    type_send = models.CharField(max_length=15)
    mark_read = models.BooleanField(default=False)


class Refer(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refer_sender')
    refer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refer_refer')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refer_receiver')
    date = models.DateTimeField(default=timezone.now)
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE)
    text = models.TextField(null=True)
    document = models.FileField(upload_to='uploads/',null=True)

    class Meta:
        ordering = ['date']


class Staff(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='staff_user')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    section = models.CharField(choices=section_choices, max_length=100)
    position = models.CharField(max_length=50)

    def __str__(self):
        return self.user.last_name
