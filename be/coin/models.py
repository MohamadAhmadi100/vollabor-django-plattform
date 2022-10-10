from django.db import models
from django.utils import timezone
from users.models import User


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=11, decimal_places=2, default=0.0)
    date_created = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}: {self.price} - {self.date_created} - Verified: {self.is_verified}"


class ExperienceBadge(models.Model):
    icon = models.ImageField(null=False, blank=False, upload_to='badges/')
    title = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.title}"


class PersonExperienceBadge(models.Model):
    badge = models.ForeignKey(ExperienceBadge, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.badge} - {self.user}"
