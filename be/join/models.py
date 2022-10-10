from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.models import field_of_study_choices, degree_choices, status_choices, refer_choices


class Applicant(models.Model):
    """
    Applicant Schema: Used for cases when someone clicked join us and send an application request
    - First Name & Last Name: User first and last name
    - Email: user email. it checks the validation when we say it's EmailField
    - Field of Study
    - status: user has to choose based on status_choices
    - Degree: user has to choose based on degree_choices
    - cv_file: pdf file that user uploads. it has to be in pdf format (mandatory)
    """
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    email = models.EmailField(null=False, blank=False, default="", verbose_name=_("Email"))
    field_of_study = models.CharField(max_length=155, choices=field_of_study_choices, null=False, blank=False,
                                      default="",
                                      verbose_name=_("Field Of Study"))
    degree = models.CharField(max_length=50, choices=degree_choices, default="", verbose_name=_("Degree"))

    phone = models.CharField(max_length=17, null=True, verbose_name=_('Phone'))
    phone_region = models.CharField(max_length=5, default='IR')

    status = models.CharField(max_length=50, choices=status_choices, verbose_name=_('Status'), default="", null=True, blank=False)
    cv_file = models.FileField(upload_to='applicants/pdf', help_text=_("It should be in PDF format"),
                               verbose_name=_("CV File"))

    is_valid = models.BooleanField(default=False)
    applicant_token = models.CharField(max_length=20, default="")
    created_time = models.DateTimeField(default=timezone.now)
    referred_by = models.CharField(max_length=200, null=True, blank=False, default="",
                                   verbose_name=_("Referred by"), choices=refer_choices,)

    # Internship
    is_internship = models.BooleanField(default=False, verbose_name=_("Internship"), null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class LegalApplicant(models.Model):
    first_name = models.CharField(max_length=100, verbose_name=_("Agent First Name"), null=True, blank=False)
    last_name = models.CharField(max_length=100, verbose_name=_("Agent Last Name"), null=True, blank=False)
    company_name = models.CharField(max_length=100, verbose_name=_("Company Name"))
    email = models.EmailField(null=False, blank=False, default="", verbose_name=_("Email"))
    phone = models.CharField(max_length=17, null=True, verbose_name=_('Phone'))
    phone_region = models.CharField(max_length=5, default='IR')

    is_valid = models.BooleanField(default=False)
    applicant_token = models.CharField(max_length=20, default="")
    created_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.company_name} - {self.first_name} {self.last_name}'


class BannedEmail(models.Model):
    banned_email = models.EmailField()


class FieldSuggestion(models.Model):
    suggested_field = models.CharField(max_length=200)
    suggested_by = models.EmailField()

    def __str__(self):
        return f"{self.suggested_field} - {self.suggested_by}"
