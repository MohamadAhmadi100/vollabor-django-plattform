from django import forms

from .models import CollaborateStaff, ApplicationDeadline


class CollaborateStaffForm(forms.ModelForm):
    cv = forms.FileField(help_text='CV format should be PDF',
                         widget=forms.FileInput(attrs={'accept': 'application/pdf'}))

    class Meta:
        model = CollaborateStaff
        fields = '__all__'

    def clean_cv(self):
        cv = self.cleaned_data.get('cv')
        if cv.content_type != 'application/pdf':
            raise forms.ValidationError('CV must be in PDF format')
        return cv


class ApplicationDeadlineForm(forms.ModelForm):

    class Meta:
        model = ApplicationDeadline
        fields = ['from_time', 'to_time']
