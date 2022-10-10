from django.contrib.auth.models import User
from django.db import models


class IndustrialManager(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class IndustrialEmail(models.Model):
    subject = models.CharField(max_length=300)
    body = models.TextField()
    category = models.CharField(max_length=300)

    def __str__(self):
        return f'{self.subject}'
