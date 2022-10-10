from django import forms
from .models import IndustrialEmail


class IndustrialEmailForm(forms.ModelForm):

    class Meta:
        model = IndustrialEmail
        fields = ['subject', 'body', 'category']
