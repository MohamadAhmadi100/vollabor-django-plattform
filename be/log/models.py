from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    log = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user} - {self.log} - {self.date}'

