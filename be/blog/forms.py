from django import forms

from blog.models import Article, Category


class PostForm(forms.ModelForm):
    description = forms.CharField(label='Description',
                   widget=forms.Textarea(attrs={'class': 'ckeditor'}))
    slug = forms.CharField()
    class Meta:
        model = Article
        fields = ['author','title','slug','category','description','thumbnail','date','status','is_top', 'suggest_time']

    def clean(self):
        super().clean()
        data=self.cleaned_data['slug'].replace(' ','')
        self.cleaned_data['slug']=data

        

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["title", "slug", "status"]