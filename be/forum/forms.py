from django import forms
from .models import Postes

class SendComment(forms.Form):
	description = forms.CharField(
		widget=forms.TextInput(),
	)

class EditForm(forms.Form):
	title = forms.CharField(
		widget=forms.Textarea(),
	)
	text = forms.CharField(
		widget=forms.Textarea(),
	)

class DeleteTopicForm(forms.Form):
	topic_id = forms.IntegerField()

class DeleteCommentForm(forms.Form):
	comment__id = forms.IntegerField()

class DeleteReplyCommentForm(forms.Form):
	replycomment_id = forms.IntegerField()




class SendReplyComment(forms.Form):
	reply_comment = forms.CharField(
		widget=forms.Textarea(),
	)
	comment_id = forms.IntegerField()


# class CreateTopic(forms.ModelForm):
# 	class Meta:
# 		model = Postes
# 		fields = ['title', 'description', 'img', 'author']

class CreateTopic(forms.Form):
	title = forms.CharField(
		widget=forms.TextInput(),
	)
	


class CreateCategoryForm(forms.Form):
	title_ = forms.CharField(
		widget=forms.TextInput(),
	)
	img = forms.ImageField()
	
	status = forms.BooleanField(
		required=False,
		label='To be displayed?'
	)




class DeleteCategory(forms.Form):
	category_id = forms.IntegerField()

class DeleteSubCategory(forms.Form):
	subcategory_id = forms.IntegerField()

class EditCategory(forms.Form):
	category__id = forms.IntegerField()
	
	text = forms.CharField(
		widget=forms.TextInput(),
	)

	img = forms.ImageField(
		required=False,)
	status = forms.BooleanField(
		required=False,
		label='To be displayed?'
	)

class EditSubCategory(forms.Form):
	subcategory__id = forms.IntegerField()

	title = forms.CharField(
		widget=forms.TextInput(),
	)
	img = forms.ImageField(
		required=False,)

	status = forms.BooleanField(
		required=False,
		label='To be displayed?'
	)




class CreateSubCategoryForm(forms.Form):
	c_category_id = forms.IntegerField()
	c_title = forms.CharField(
		widget=forms.TextInput(),
	)
	
	img = forms.ImageField()
	
	c_status = forms.BooleanField(
		required=False,
		label='To be displayed?'
	)

