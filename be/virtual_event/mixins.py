from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from users.models import Role


class ManagerMixin(PermissionRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        roles=Role.objects.filter(user=request.user)
        access=False
        if request.user.is_superuser:
            access=True
        else:
            for role in roles:
                if role.position == 'virtual manager':
                    access=True

        if access:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect_to_login(self.request.get_full_path(),self.get_login_url(),self.get_redirect_field_name())

class ExpertManagerMixin(PermissionRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        roles=Role.objects.filter(user=request.user)
        access=False
        if request.user.is_superuser:
            access=True
        else:
            for role in roles:
                if role.position == 'virtual manager' or role.position == 'virtual expert':
                    access=True
        if access:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect_to_login(self.request.get_full_path(),self.get_login_url(),self.get_redirect_field_name())