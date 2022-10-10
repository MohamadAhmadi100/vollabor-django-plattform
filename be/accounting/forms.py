from django import forms
from .models import *
from email_app.models import Country


class BankInfoForm(forms.ModelForm):
    firstname=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    lastname=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    shaba_acoount=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    account_number=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    card_number=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))

    class Meta:
        model=User_bank_info
        fields=['firstname','lastname','shaba_acoount','account_number','card_number']

class RequestMoneyForm(forms.ModelForm):
    amount=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))

    class Meta:
        model=Request_money
        fields=['amount','is_done']


# class SelectCountry(forms.Form):
#     CHOICES = ()
#     for c in Country.objects.all():
#         CHOICES=CHOICES+((c.title,c.title),)
   
#     country=forms.ChoiceField(choices=CHOICES,label='Country',widget=forms.Select(attrs={'class':'form-control'}))


class CreateAgencyForm(forms.ModelForm):
    info=forms.CharField(widget=forms.Textarea(attrs={'rows':3}))
    location=forms.CharField(widget=forms.Textarea(attrs={'rows':3}))

    class Meta:
        model=Agency
        fields='__all__'

    def _init__(self,*args,**kwargs):
        super(CreateAgencyForm,self).__init__(*args,**kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

# class CentralRequestForm(forms.ModelForm):
#     origin_agency=forms.IntegerField(widget=forms.HiddenInput())
#     class Meta:
#         model=CentralRequestPayment
#         fields=['destination_agency','amount']
#         def __init__(self,*args,**kwargs):
#             super(CentralRequestForm,self).__init__(*args,**kwargs)
#             for visible in self.visible_fields():
#                 visible.field.widget.attrs['class'] = 'form-control'