from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .models import Applicant, LegalApplicant


def validate_file_extension(value):
    if not value.name.endswith('.pdf'):
        raise ValidationError(u'Error message')


class ApplicantForm(forms.ModelForm):
    """
    Applicant Form that we show on join us page
    we can specify what to show by changing fields element in Meta class
    (elements should be defined inside Applicant Model first)
    """
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'youremail@example.com'}),
                             label=_("Email"))
    # cv_file = forms.FileField(help_text=mark_safe(
    #     '<a href="/static/CV_Sample.docx" target="_blank">CV Sample</a><p>CV format should be PDF</p>'
    # ),
    #     widget=forms.FileInput(attrs={'accept': 'application/pdf'}))

    # is_internship = forms.BooleanField(label='Internship', widget=forms.CheckboxInput(attrs=
    #                                                                                   {'class': "ml-1"}), required=False)
                                                                                
    phone=forms.CharField(widget=forms.TextInput(attrs={'id': 'phone'}))
    phone_region=forms.CharField(max_length=5, widget=forms.TextInput(attrs={'id': 'natural_phone_region','class': 'd-none','value':'us'}))


    class Meta:
        model = Applicant
        fields = ['first_name', 'last_name', 'email', 'phone_region','phone', 'field_of_study', 'degree']


class LegalApplicantForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'youremail@example.com'}),
                             label=_("Email"))

    class Meta:
        model = LegalApplicant
        fields = ['first_name', 'last_name', 'company_name', 'email', 'phone']
