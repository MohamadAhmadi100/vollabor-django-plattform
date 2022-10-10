from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_jalali.db import models as jmodels

from ivc_website.models import Project


class CollaborateStaff(models.Model):
    first_name = models.CharField(max_length=200, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=200, verbose_name=_("Last Name"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    email = models.EmailField(verbose_name=_("Email"), unique=True)
    phone_region = models.CharField(max_length=5, null=True, blank=False)
    phone = models.CharField(max_length=50, verbose_name=_("Phone number"), null=True, blank=False)
    cv = models.FileField(verbose_name=_("CV"), upload_to='collaborate_staff/', help_text=_('Should be in PDF format'))
    about = models.TextField(verbose_name=_("Why do you think you're eligible for this?"))
    time_spend = models.PositiveIntegerField(verbose_name=_("The amount of hour you can spend per day"))
    is_member = models.BooleanField(verbose_name=_("Are you a company member?"))
    without_project = models.BooleanField(default=False)
    application_date = models.DateTimeField(default=timezone.now, blank=True)
    recommendation = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ['-application_date']


class CollaborateStaffProject(models.Model):
    staff = models.ForeignKey(CollaborateStaff, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.staff} - {self.project}'


class CollaborateStaffInterest(models.Model):
    staff = models.ForeignKey(CollaborateStaff, on_delete=models.CASCADE)
    interest = models.CharField(max_length=150)

    def __str__(self):
        return f'{self.staff} - {self.interest}'


class StaffManager(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class ApplicationDeadline(models.Model):
    type = models.CharField(max_length=100, default="Course", unique=True)
    from_time = jmodels.jDateTimeField(verbose_name="From")
    to_time = jmodels.jDateTimeField(verbose_name="To")

    def __str__(self):
        return f"{self.type}: from {self.from_time} to {self.to_time}"
