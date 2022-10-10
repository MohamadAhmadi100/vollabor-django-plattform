from django.http import Http404
from .models import Postes, TopicComment
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect
class FieldsMixin():
	def dispatch(self, request, *args, **kwargs):
		if request.user.is_superuser:
			self.fields = ['author','title','description','categorys','hits']
		else :
			self.fields = ['title','description','categorys']
		return super().dispatch(request, *args, **kwargs)

class FormMixnis():
	def form_valid(self, form):
		if self.request.user.is_superuser:
			form.save()
		else:
			self.obj = form.save(commit=False)
			self.obj.author = self.request.user
		return super().form_valid(form)

class AuthenticateUserMixins():
	def dispatch(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return super().dispatch(request, *args, **kwargs)
		else:
			return redirect('login')


class DeleteMixins():
	def dispatch(self, request, pk, *args, **kwargs):
		post = get_object_or_404(Postes, pk=pk)
		if request.user.is_superuser or post.author == request.user or request.user.has_perm('forum.delete_postes'):
			return super().dispatch(request, *args, **kwargs)
		else:
			raise Http404("You can't see this page.")

class DeleteCommentMixins():
	def dispatch(self, request, pk, *args, **kwargs):
		comment = get_object_or_404(TopicComment, pk=pk)
		if request.user.is_superuser or comment.user == request.user or comment.topic.author == request.user or request.user.has_perm('forum.delete_postes'):
			return super().dispatch(request, *args, **kwargs)
		else:
			raise Http404("You can't see this page.")


class DeleteCatMixins():
	def dispatch(self, request, pk, *args, **kwargs):
		if request.user.is_superuser or request.user.has_perm('forum.delete_category'):
			return super().dispatch(request, *args, **kwargs)
		else:
			raise Http404("You can't see this page.")
class FieldsCatMixin():
	def dispatch(self, request, *args, **kwargs):
		if request.user.is_superuser or request.user.has_perm('forum.add_category'):
			self.fields = ['sub_category','title','slug','description','status']
		else:
			raise Http404("You can't see this page.")
		return super().dispatch(request, *args, **kwargs)