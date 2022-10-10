from django.urls import reverse_lazy
from django.db.models import Count, Q
from workshop.models import Workshop
from users.models import MemberProfile
from datetime import datetime, timedelta
from research.models import ResearchProject
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from seo.models import UserFootprint
from .mixins import (
	DeleteMixins, DeleteCatMixins, FieldsCatMixin, FieldsMixin, 
	FormMixnis, AuthenticateUserMixins, DeleteCommentMixins
	)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .forms import (
	SendComment, SendReplyComment, CreateTopic, CreateCategoryForm, EditForm, 
	DeleteTopicForm, DeleteCommentForm, DeleteReplyCommentForm
	)
from .models import *
# Create your views here.

@login_required
def detail_topic(request, pk):
	post = get_object_or_404(Postes, pk=pk)
	History.objects.create(user=request.user.id, topic=post, date_add_to_history=datetime.now())
	if request.user.is_authenticated:
		create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)

	views = ViewTopic.objects.filter(user=request.user, topic=post).count()

	if views == 0:
		ViewTopic.objects.create(user=request.user, topic=post)
	
		

	if request.method == 'POST':
		#create comment
		form = SendComment(request.POST, request.FILES)
		if form.is_valid():

			description = form.cleaned_data.get("description")

			new_from = TopicComment.objects.create(topic=post ,description=description, user=request.user)
			return redirect('forum:detail-title', post.pk)

			
		# reply from
		form_reply = SendReplyComment(request.POST)
		if form_reply.is_valid():
			reply_comment = form_reply.cleaned_data.get("reply_comment")
			comment_id = form_reply.cleaned_data.get("comment_id")

			new_from = ReplyComment.objects.create(reply_comment=reply_comment, topic=post, comment_int=comment_id, user=request.user)
			return redirect('forum:detail-title', post.pk)

			
		# Edit topic
		form_edit_topic = CreateTopic(request.POST, )
		if form_edit_topic.is_valid():
			title = form_edit_topic.cleaned_data.get("title")

			post.title = title
			post.save()
			return redirect('forum:detail-title', post.pk)
			
		# Delete topic
		form_delete_topic = DeleteTopicForm(request.POST, )
		if form_delete_topic.is_valid():
			topic_id = form_delete_topic.cleaned_data.get("topic_id")
			print('post.deleted', post.deleted)
			post.deleted = True
			post.save()
			print('post.deleted', post.deleted)
			print('post.deleted', post.deleted)
			return redirect('forum:category-topic', post.categorys.slug)
			
		# Delete comment
		form_delete_comment = DeleteCommentForm(request.POST, )
		if form_delete_comment.is_valid():
			comment__id = form_delete_comment.cleaned_data.get("comment__id")

			obj_comment = TopicComment.objects.get(pk=comment__id)
			obj_comment.delete()
			return redirect('forum:detail-title', post.pk)

			
		# Delete reply comment
		form_delete_reply_comment = DeleteReplyCommentForm(request.POST, )
		if form_delete_reply_comment.is_valid():
			replycomment_id = form_delete_reply_comment.cleaned_data.get("replycomment_id")

			obj_comment = ReplyComment.objects.get(id=replycomment_id)
			obj_comment.delete()
			return redirect('forum:detail-title', post.pk)

	else:
		form = SendComment
		form_reply = SendReplyComment
		form_edit_topic = EditForm	

	comment = TopicComment.objects.all()
	rep_comment = ReplyComment.objects.all()

	context = {
		'object': post,
		'form': form,
		'form_reply': form_reply,
		'form_edit_topic': form_edit_topic,
		'comment_forum': TopicComment.objects.filter(topic=post).order_by('-created'),
		'comment_forum_count': TopicComment.objects.filter(topic=post).count(),
		'ReplyComment': ReplyComment.objects.all().order_by('-created'),
	}

	return render(request, 'topic.html', context)




class CategoryList(ListView):
	paginate_by = 20
	global category
	category = MainCategory.objects.filter(status=True)
	queryset = category
	template_name = 'categories.html'
	def get_context_data(self, **kwargs):
		if self.request.user.is_authenticated:
			create_user_footprint = UserFootprint.objects.create(user=self.request.user, url=self.request.path)
		context = super().get_context_data(**kwargs)
		context['category'] = category
		return context



class CategorySubList(ListView):
	template_name = 'subcategories.html'
	paginate_by = 15
	def get_queryset(self):
		global category
		slug = self.kwargs.get('slug')
		category = get_object_or_404(MainCategory, slug=slug)
		return category.childern.filter(status=True)
	def get_context_data(self, **kwargs):
		if self.request.user.is_authenticated:
			create_user_footprint = UserFootprint.objects.create(user=self.request.user, url=self.request.path)
		context = super().get_context_data(**kwargs)
		context['category'] = category
		return context

# def category_topic_create(request, slug):
# 	category = get_object_or_404(Category.objects.Active(), slug=slug)
# 	if request.method == 'POST':
# 		data = request.POST.copy()
# 		data['author'] = request.user
# 		form = CreateTopic(data, request.FILES)
# 		if form.is_valid():
# 			post = form.save(commit=False)
# 			post.save()
# 			post.categorys.add(category.id)
# 			return redirect('forum:category-topic', category.slug)
# 		else:
# 			return HttpResponse(form.errors)
# 	else:
# 		form = CreateTopic
		
# 	context = {
# 	"form": form,
# 	"topics": category.postes.all(),
# 	}

# 	return render(request, 'sub-category-list.html', context)

def category_topic_create(request, slug):
	category = get_object_or_404(Category.objects.Active(), slug=slug)
	if request.method == 'POST':
		title = request.POST.get("text")

		create_topic = Postes.objects.create(
			author=request.user, title=title, categorys=category
			)

		return redirect("forum:category-topic", category.slug)
	else:
		form = CreateTopic
		
	context = {
	"form": form,
	'category': category,
	"topics": category.postes.filter(deleted=False),
	}
	if request.user.is_authenticated:
		create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)
	return render(request, 'sub-category-list.html', context)
	


class HistoryList(LoginRequiredMixin, ListView):
	paginate_by = 30
	template_name = 'history.html'
	model = History
	def get_queryset(self):
		request = self.request
		return History.objects.filter(user=request.user.id).all().distinct().order_by('-date_add_to_history')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['images'] = MemberProfile.objects.all()
		return context

class EditCategory(LoginRequiredMixin, DeleteCatMixins, UpdateView):
	template_name = 'edit-category.html'
	model = Category
	fields = ['sub_category', 'title', 'slug', 'description', 'img', ]


def like_topic(request, pk):
	if request.method == 'POST':
		status = request.POST.get('status')

		if status == 'topic':
			likes = Like.objects.filter(user=request.user, topic_id=pk,).count()

			if likes == 0:
				create_obj = Like.objects.create(user=request.user, topic_id=pk, )
			else:
				obj_like = Like.objects.get(user=request.user, topic_id=pk,)
				if obj_like.status == 'true':
					obj_like.status = 'false'
				else:
					obj_like.status = 'true'
				obj_like.save()
			return redirect("forum:detail-title", pk)

		elif status == 'comment':
			likes = Like.objects.filter(user=request.user, comment_id=pk,).count()

			if likes == 0:
				create_obj = Like.objects.create(user=request.user, comment_id=pk, )
				return redirect("forum:detail-title", create_obj.comment.topic.pk)
			else:
				obj_like = Like.objects.get(user=request.user, comment_id=pk,)
				if obj_like.status == 'true':
					obj_like.status = 'false'
				else:
					obj_like.status = 'true'
				obj_like.save()
				return redirect("forum:detail-title", obj_like.comment.topic.pk)

		elif status == 'replycomment':
			likes = Like.objects.filter(user=request.user, replycomment_id=pk,).count()

			if likes == 0:
				create_obj = Like.objects.create(user=request.user, replycomment_id=pk, )
				return redirect("forum:detail-title", create_obj.replycomment.topic.pk)
			else:
				obj_like = Like.objects.get(user=request.user, replycomment_id=pk,)
				if obj_like.status == 'true':
					obj_like.status = 'false'
				else:
					obj_like.status = 'true'
				obj_like.save()
				return redirect("forum:detail-title", obj_like.replycomment.topic.pk)



def dislike_comment(request, pk):
	if request.method == 'POST':
		status = request.POST.get('status')

		if status == 'comment':
			Dislikes = DisLike.objects.filter(user=request.user, comment_id=pk,).count()

			if Dislikes == 0:
				create_obj = DisLike.objects.create(user=request.user, comment_id=pk, )
				return redirect("forum:detail-title", create_obj.comment.topic.pk)
			else:
				obj_like = DisLike.objects.get(user=request.user, comment_id=pk,)
				if obj_like.status == 'true':
					obj_like.status = 'false'
				else:
					obj_like.status = 'true'
				obj_like.save()
				return redirect("forum:detail-title", obj_like.comment.topic.pk)

		elif status == 'replycomment':
			Dislikes = DisLike.objects.filter(user=request.user, replycomment_id=pk,).count()

			if Dislikes == 0:
				create_obj = DisLike.objects.create(user=request.user, replycomment_id=pk, )
				return redirect("forum:detail-title", create_obj.replycomment.topic.pk)
			else:
				obj_like = DisLike.objects.get(user=request.user, replycomment_id=pk,)
				if obj_like.status == 'true':
					obj_like.status = 'false'
				else:
					obj_like.status = 'true'
				obj_like.save()
				return redirect("forum:detail-title", obj_like.replycomment.topic.pk)
