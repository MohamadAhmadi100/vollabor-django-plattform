from django import forms
from .models import  VirtualEvent,Timetable,Workshop,Course,Seminar



class VirtualEventForm(forms.ModelForm):   
    class Meta:
        model = VirtualEvent
        fields = ['title','price','type',]
     
