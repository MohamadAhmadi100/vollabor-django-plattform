from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from dashboard.utilities import user_has_memberprofile
from coin import param
from users.models import User
from accounting.models import Invoice


class InternationalOrder(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE, null=True, blank=False)
    date_created = models.DateTimeField(default=timezone.now)
    purchased_amount = models.DecimalField(max_digits=11, decimal_places=2, default=0.0)
    payment_intent = models.CharField(max_length=100, null=True, blank=False)
    has_completed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.payment_intent}'


@receiver(post_save, sender=InternationalOrder)
def add_notification_for_news_managers(sender, instance, created, **kwargs):
    """
    Adding responsibility fees after purchasing them
    """
    if instance.has_completed:
        if user_has_memberprofile(instance.user):
            user_profile = instance.user.memberprofile
            user_profile.balance += instance.purchased_amount / param.responsibility_fee_value
            user_profile.save()

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE, null=True, blank=False)
    id_pay = models.CharField(max_length=100, unique=True, null=True)
    paymented = models.IntegerField(default=0, null=True)
    country = models.CharField(max_length=100, null=True)
    amount = models.FloatField(null=True, )
    pymeny_method = models.CharField(max_length=100, null=True)
    gsp = models.FloatField(null=True, )
    pst = models.FloatField(null=True, )
    additional_fee = models.FloatField(null=True, )
    total = models.IntegerField(null=True, )
    zarinpal_amount = models.IntegerField(null=True, )
    success_date = models.DateTimeField(default=None, null=True, blank=True)
    back_url=models.CharField(max_length=100,null=True,blank=True)
    invoice=models.ForeignKey(Invoice,on_delete=models.CASCADE,null=True)
    merchant=models.CharField(max_length=36,null=True)
    
    

class Dollar(models.Model):
    Automatically = models.BooleanField(default=True, null=True)
    price = models.IntegerField(null=True)
    last_editor = models.ForeignKey(User, on_delete=CASCADE, null=True)
    created = models.DateTimeField(null=True, auto_now_add=True)
