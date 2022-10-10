from django.http import Http404

class CreateCategoryMixin():
	def dispatch(self, request, *args, **kwargs):
		if self.request.user.is_superuser or self.request.user.adrole.create_category == True:
			self.fields = ['title',]
		else:
			raise Http404("You can't see this page.")
		return super().dispatch(request, *args, **kwargs)


class CreateCompanyMixin():
	def dispatch(self, request, *args, **kwargs):
		if self.request.user.is_superuser or self.request.user.has_perm('email_app.view_category'):
			self.fields = [
			'company_name', 'country', 'state', 'city', 'street_number', 'building_number', 
			'unit', 'zip_code', 'size', 'company_website_link', 'outsource', 'services', 'products', 
			'current_need', 'future_need', 
			]
		else:
			raise Http404("You can't see this page.")
		return super().dispatch(request, *args, **kwargs)

class UpdateMixnis():
	def form_valid(self, form):
		self.obj = form.save(commit=False)
		request_user = self.request.user
		request_user = str(request_user)
		self.obj.last_editor += request_user
		self.obj.last_editor += ', '
		return super().form_valid(form)



class CreateCategoryTemplateMixin():
	def dispatch(self, request, *args, **kwargs):
		if self.request.user.is_superuser or self.request.user.adrole.create_template_category == True:
			self.fields = ['title' ,'slug',]
		else:
			raise Http404("You can't see this page.")
		return super().dispatch(request, *args, **kwargs)


class CreatorMixnis():
	def form_valid(self, form):
		self.obj = form.save(commit=False)
		self.obj.creator = self.request.user
		return super().form_valid(form)

class UploadImgMixin():
	def dispatch(self, request, *args, **kwargs):
		if self.request.user.is_superuser or self.request.user.adrole.upload_image == True:
			self.fields = ['title' ,'img' ]
		else:
			raise Http404("You can't see this page.")
		return super().dispatch(request, *args, **kwargs)
		
class UpdateEmailMixin():
	def dispatch(self, request, *args, **kwargs):
		if self.request.user.is_superuser or self.request.user.adrole.edit_delete_email == True:
			self.fields = ['company_agent_first_name','company_agent_surname','agent_position','agent_academic_degree','gender','agent_email_address','tags']
		else:
			raise Http404("You can't see this page.")
		return super().dispatch(request, *args, **kwargs)

class CreateTemplateMixin():
	def dispatch(self, request, *args, **kwargs):
		if self.request.user.is_superuser or self.request.user.has_perm('email_app.view_category'):
			self.fields = ['template', 'img', 'title', 'description', 'categories']
		else:
			raise Http404("You can't see this page.")
		return super().dispatch(request, *args, **kwargs)


class DeleteMixins():
	def dispatch(self, request, pk, *args, **kwargs):
		if request.user.is_superuser or request.user.has_perm('email_app.view_category'):
			return super().dispatch(request, *args, **kwargs)
		else:
			raise Http404("You can't see this page.")