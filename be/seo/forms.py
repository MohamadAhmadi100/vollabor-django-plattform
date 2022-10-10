from django import forms

from seo.models import RobotsMeta, TitleAndDescription


class RobotsForm(forms.ModelForm):
    class Meta:
        model = RobotsMeta
        fields = '__all__'


class TitleDescriptionForm(forms.ModelForm):
    class Meta:
        model = TitleAndDescription
        fields = '__all__'
