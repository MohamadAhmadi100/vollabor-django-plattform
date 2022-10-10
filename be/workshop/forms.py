from django import forms
from .models import Workshop,SubField, Guarante, LandingPage,Adverstiment
from django.core.exceptions import ValidationError


class WorkshopTempForm(forms.ModelForm):
    guaranteed = forms.ModelChoiceField(queryset=Guarante.objects.all(), required=False)
    proof_file = forms.FileField(required=False)
    image = forms.ImageField(required=False)
    sub_field = forms.ModelChoiceField(queryset=SubField.objects.all(), required=False)
    prev_experience = forms.CharField(widget=forms.Textarea,required=False)
    capacity = forms.IntegerField(required=False)
    date = forms.DateField(required=False)
    time_to_start = forms.TimeField(required=False)
    duration = forms.CharField(required=False)
    
    class Meta:
        model = Workshop
        fields = ['top_user','guaranteed','title','time_to_start','date','duration','main_field','sub_field','image','load_pdf','description','address','prev_experience',
        'work_with_us','work_with_others','proof_file','language','speaker','suggest_country','keyword','skills','time_zone','capacity', 'is_online']

    def __init__(self, *args, **kwargs):
        super(WorkshopTempForm, self).__init__(*args, **kwargs)
        self.fields['guaranteed'].empty_label = "No guarantee"

        """self.fields['sub_field'].queryset = SubField.objects.all()

        if 'main_field' in self.data:
            try:
                field_id = int(self.data.get('main_field'))
                self.fields['sub_field'].queryset = SubField.objects.filter(parent_id=field_id).order_by('title')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        else:
            self.fields['sub_field'].queryset = SubField.objects.none()"""
            
class Landingpageform(forms.ModelForm):
    direction_CHOICES=[('ltr','left to right'),('rtl','right to left')]
    direction= forms.CharField(label='Choose direction', widget=forms.Select(choices=direction_CHOICES))
    title=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label='Title')
    coursetitles_title=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label='Title for course titles')
    coursetitles = forms.CharField(label='Course titles',widget=forms.Textarea(attrs={'class': 'ckeditor form-control'}))
    courseclients_title=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label=' Title for Audiences')
    courseclients=forms.CharField(label='Audiences',widget=forms.Textarea(attrs={'class': 'ckeditor form-control'}))
    certificate_title=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label='title for Certificate')
    certificatedesc=forms.CharField(label='Certificate description',widget=forms.Textarea(attrs={'class': 'ckeditor form-control'}))
    content=forms.CharField(label='Course summary',widget=forms.Textarea(attrs={'class': 'ckeditor form-control'}))
    coursespeakers_title=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label='Title for Introducing the spokespersons')
    coursespeakers=forms.CharField(label='Resume of Speakers',widget=forms.Textarea(attrs={'class': 'ckeditor form-control'}))
    registeration_title=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),label='Title for Registration steps')
    registeration_content=forms.CharField(label='Registration steps',widget=forms.Textarea(attrs={'class': 'ckeditor form-control'}))
    logo_image=forms.FileField(label="Logo's image",required=False)
    banner_image=forms.FileField(label='Banner image')
    

    class Meta:
        model = LandingPage
        fields=[
        'direction',
        'title','coursetitles_title', 'coursetitles','courseclients_title','courseclients','certificate_title','certificatedesc',
        'content','coursespeakers_title','coursespeakers','registeration_title','registeration_content','logo_image','banner_image'
        ]

class Advertisingform(forms.ModelForm):
    title=forms.CharField(widget=forms.Textarea(attrs={'class':'form-control','rows':2}),label='Title',required=True)
    coursetitles = forms.CharField(label='Course titles',widget=forms.Textarea(attrs={'class': 'ckeditor form-control','rows':2}),required=True)
    courseclients=forms.CharField(label='Audiences',widget=forms.Textarea(attrs={'class': 'ckeditor form-control','rows':2}),required=True)
    certificatedesc=forms.CharField(label='Certificate description',widget=forms.Textarea(attrs={'class': 'ckeditor form-control','rows':2}),required=True)
    content=forms.CharField(label='Course summary',widget=forms.Textarea(attrs={'class': 'ckeditor form-control','rows':2}),required=True)
    coursespeakers=forms.CharField(label='Resume of Speakers',widget=forms.Textarea(attrs={'class': 'ckeditor form-control','rows':2}),required=True)
    logo_image=forms.ImageField(label="Logo's image",required=False)
    contracts=forms.FileField(label="Contract",required=False)
    

    class Meta:
        model = Adverstiment
        # fields=[
        # 'title','coursetitles','courseclients','certificatedesc',
        # 'content','coursespeakers','logo_image','contracts'
        # ]
        exclude=['workshop']

    # def clean(self):
    #         super().clean()
    #         image=self.cleaned_data.get('logo_image')
    #         contract=self.cleaned_data.get('contracts')
    #         print(image)
    #         print(image)
    #         print(image)
    #         print(image)
    #         print(image)
    #         print(image)
    #         print(image)
            # if image.size > (500 * 500 * 1):
            #     self.add_error('image','Your image is too large. Max size is 0.5 MB')
            # if contract.size > (500 * 500 * 1):
            #         self.add_error('contract','Your file is too large. Max size is 0.5 MB')
