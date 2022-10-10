from django.contrib.auth.models import User
from django.db import models


class CompetitionManager(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}'
