from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Question(models.Model):
    question = models.TextField()

    # User is authenticated
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # User is not authenticated
    full_name = models.CharField(max_length=200, null=True, blank=False)
    email = models.EmailField(null=True, blank=True)

    date_created = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(null=True)

    def __str__(self):
        return f"{self.question}"


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()
    is_verified = models.BooleanField(null=True)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} answered {self.question}"


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.question}"


class AnswerDislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.question}"


class QuestionAnswerManager(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}"
