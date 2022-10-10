from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import ClearableFileInput
from django.utils.translation import gettext_lazy as _

from .models import MemberProfile, LegalProfile
import datetime


class DateInput(forms.DateInput):
    """
    Date input class which is a widget we can use to show date format input instead of plain text in our form
    """
    input_type = 'date'


class CustomClearableFileInput(ClearableFileInput):
    """
    this is a custom clearable file input. by default django has a file input with two sections:
    -currently: there is a url in front of it and when we click to open. it open uploaded file
    -change: you can click that button and and change your file

    the problem is by clicking on currently url, it opens the link in the same page. so I added this to open it
    on a new tab (by just adding target="_blank")
    """
    template_name = 'users/custom_file_input.html'


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileUpdateForm(forms.ModelForm):
    birthday = forms.DateField(widget=DateInput, label=_('Birthday'))
    cv_file = forms.FileField(widget=CustomClearableFileInput(), label=_('CV File'))

    class Meta:
        model = MemberProfile
        fields = ['field_of_study', 'status', 'degree', 'interest', 'about_me', 'cv_file',
                  'birthday', 'gender', 'time_can_spend_per_day', 'phone_region', 'phone', 'university', 'city',
                  'country',
                  'skype']

    def clean(self):
        cleaned_data = super().clean()
        time_can_spend_per_day = cleaned_data.get("time_can_spend_per_day")
        if time_can_spend_per_day < 0 or time_can_spend_per_day > 24:
            self.add_error('time_can_spend_per_day',
                           ValidationError("Time that you spend per day should be a amount between 0 and 24"))


class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = LegalProfile
        fields = ['phone_region', 'phone']


class SkypeForm(forms.ModelForm):
    skype = forms.CharField(label="Skype ID*", required=False, widget=forms.TextInput(attrs={
        'title': "This field is required",
    }))

    class Meta:
        model = LegalProfile
        fields = ['skype']


class PreferenceForm(forms.ModelForm):
    class Meta:
        model = LegalProfile
        fields = ['contact_preference']


class LegalProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = LegalProfile
        fields = ['company_name', 'work_area', 'about_company', 'phone', 'fax', 'city', 'country', 'street', 'zip_code',
                  'registration_number', 'skype', 'phone_region', 'instagram', 'linkedin', 'telegram']



class LegalImageUpdateForm(forms.ModelForm):
    image = forms.ImageField(widget=CustomClearableFileInput(), label=_('Image'),
        required=False
        )
    
    class Meta:
        model = LegalProfile
        fields = ['image']



class ImageUpdateForm(forms.ModelForm):
    image = forms.ImageField(widget=CustomClearableFileInput(), label=_('Image'),
        required=False
        )
        
    class Meta:
        model = MemberProfile
        fields = ['image']
        


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control d-block', 'placeholder': 'نام کاربری را وارد کنید.'}),
        label='نام کاربری'
        )

    password = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control d-block', 'placeholder': 'رمز عبور خود را وارد کنید.'}),
        label='رمز عبور'
        )
    remember_me = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-control'}), 
        required=False, 
        label='مرا بخاطر بسپارید')

