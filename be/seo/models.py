from django.contrib.auth.models import User
from django.db import models

meta_index_choices = (
    ('index', 'index'),
    ('noindex', 'noindex'),
)
meta_follow_choices = (
    ('follow', 'follow'),
    ('nofollow', 'nofollow'),
)


class SEO(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}"


class RobotsMeta(models.Model):
    index = models.CharField(max_length=7, choices=meta_index_choices, default='index')
    follow = models.CharField(max_length=8, choices=meta_follow_choices, default='follow')
    url = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f'{self.url} -> {self.index}, {self.follow}'


class TitleAndDescription(models.Model):
    title = models.CharField(max_length=300, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    keyword = models.TextField(null=True, blank=True)
    url = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f'{self.url}'

class UserFootprint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_footprint')
    url = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)