from django.db import models


class FAQ(models.Model):
    question = models.CharField(max_length=300, null=True, blank=False)
    answer = models.TextField()

    def __str__(self):
        return f"{self.question}"
