from asyncio.windows_events import NULL
from django.db.models import Max
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from dashboard.utilities import user_has_memberprofile
from log.models import Log
from .forms import *
from .models import interest_choices, TopSupervisor
from django.contrib.auth.views import LoginView, PasswordResetView
from .custom_login import CustomAuthenticationForm
from ivc_project.recaptcha_validator import is_recaptcha_valid
from django.contrib.auth import login as auth_login
from request.models import BadgeRequest
from workshop.models import Users_Workshops


def members(request):
    context = {
        'professor_numbers': MemberProfile.objects.filter(status='Professor').count(),
        'postdoc_numbers': MemberProfile.objects.filter(status='Post-Doctoral').count(),
        'phd_numbers': MemberProfile.objects.filter(degree='Doctoral degree').count(),
        'master_numbers': MemberProfile.objects.filter(degree="Master's degree").count(),
        'bachelor_numbers': MemberProfile.objects.filter(degree="Bachelor's degree").count(),
        'total_numbers': MemberProfile.objects.all().count(),
        'top_supervisors': TopSupervisor.objects.all()
    }
    return render(request, 'users/members.html', context)


@login_required
def profile(request):
    """
    Profile view: user can change his info on this view it has two form one created from User model the other from
    MemberProfile Model
    """
    if user_has_memberprofile(request.user):
        if request.method == "POST":
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.memberprofile)
            img_form = ImageUpdateForm(request.POST, request.FILES, instance=request.user.memberprofile)
            if u_form.is_valid() and p_form.is_valid() and img_form.is_valid():
                cv_file = p_form.cleaned_data.get('cv_file')  # get cv file
                try:
                    if cv_file.content_type == 'application/pdf':  # if cv file format is pdf
                        u_form.save()
                        p_form.save()
                        img_form.save()
                        messages.success(request, f'Your account has been updated')
                    else:
                        messages.error(request, f"You're CV must be in PDF format")
                except AttributeError:  # in case user doesn't change his CV:
                    u_form.save()
                    p_form.save()
                    img_form.save()
                    messages.success(request, f'Your account has been updated')

                if 'next' in request.GET:
                    return HttpResponseRedirect(request.GET['next'])  # redirect to next page (which is dashboard)
                else:
                    return HttpResponseRedirect(request.path_info)  # redirect to the same page
            else:
                messages.error(request, f"Some fields have problem, please scroll down and see what they are")

        else:
            u_form = UserUpdateForm(instance=request.user)
            p_form = ProfileUpdateForm(instance=request.user.memberprofile)
            img_form = ImageUpdateForm(instance=request.user.memberprofile)

    else:
        if request.method == "POST":
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = LegalProfileUpdateForm(request.POST, instance=request.user.legalprofile)
            img_form = LegalImageUpdateForm(request.POST, request.FILES, instance=request.user.legalprofile)

            if u_form.is_valid() and p_form.is_valid() and img_form.is_valid():
                u_form.save()
                p_form.save()
                img_form.save()
                messages.success(request, f'Your account has been updated')

                if 'next' in request.GET:
                    return HttpResponseRedirect(request.GET['next'])  # redirect to next page (which is dashboard)
                else:
                    return HttpResponseRedirect(request.path_info)  # redirect to the same page

            else:
                messages.error(request, f"Some fields have problem, please scroll down and see what they are")

        else:
            u_form = UserUpdateForm(instance=request.user)
            p_form = LegalProfileUpdateForm(instance=request.user.legalprofile)
            img_form = LegalImageUpdateForm(instance=request.user.legalprofile)
    
    if BadgeRequest.objects.filter(user = request.user, status__in = ['Accept', 'Accept-manager']).count() >= 1:
        badges = BadgeRequest.objects.filter(user = request.user, status__in = ['Accept', 'Accept-manager'])
    else:
        badges = None
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'img_form': img_form,
        'badges': badges,
        'memberprofile': request.user.memberprofile,
        'certificates':Users_Workshops.objects.filter(user=request.user,is_paid=True).exclude(certificate=None).all()
    }
    if user_has_memberprofile(request.user):
        context['selected_interests'] = request.user.memberprofile.interest
    return render(request, 'users/profile.html', context)


def member_profile(requests, primary_key):
    try:
        selected_supervisor = TopSupervisor.objects.get(pk=primary_key)
    except:
        return render(requests, 'ivc_website/404.html')

    return render(requests, 'users/member-profile.html', {'profile': selected_supervisor})


@login_required
def reset_password_profile(request):
    """
    Reset password view: It uses PasswordChangeForm created by django to change user password
    """
    if request.POST:
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user_password = password_form.save()
            update_session_auth_hash(request, user_password)  # Important!
            messages.success(request, f'Password has changed successfully')

            return redirect('profile-page')
    else:
        password_form = PasswordChangeForm(request.user)

    return render(request, 'users/change_password.html', {'form': password_form})



class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        is_valid = is_recaptcha_valid(self.request)
        if is_valid:
            """Security check complete. Log the user in."""
            auth_login(self.request, form.get_user())
            Log(user=form.get_user(), log='logged in').save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            messages.error(self.request, 'reCAPTCHA is invalid.')
            return HttpResponseRedirect(self.request.path_info)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard-page')

    if request.method == 'POST':

        is_valid = is_recaptcha_valid(request)
        if is_valid:
            form = LoginForm(request.POST or None)
            if form.is_valid():
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                remember_me = form.cleaned_data.get("remember_me")

                if not remember_me:
                    request.session.set_expiry(0)

                user = authenticate(request, username=username, password=password)

                if user is not None:
                    login(request, user)
                    return redirect('dashboard-page')
                else:
                    messages.error(request, 'The email or password is invalid.')
        else:
            messages.error(request, 'reCAPTCHA is invalid.')
            return HttpResponseRedirect(request.path_info)
    else:
        form = LoginForm()

    context = {
        'form': form
    }
    return render(request, 'users/login.html', context)

class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        is_valid = is_recaptcha_valid(self.request)
        if is_valid:
            """Security check complete. do password change request."""
            submitted_email = form.cleaned_data['email']
            if '@gmail.com' in submitted_email:
                form.cleaned_data['email'] = f'{submitted_email.split("@")[0].replace(".", "")}@gmail.com'
            opts = {
                'use_https': self.request.is_secure(),
                'token_generator': self.token_generator,
                'from_email': self.from_email,
                'email_template_name': self.email_template_name,
                'subject_template_name': self.subject_template_name,
                'request': self.request,
                'html_email_template_name': self.html_email_template_name,
                'extra_email_context': self.extra_email_context,
            }
            form.save(**opts)
            return super().form_valid(form)
        else:
            messages.error(self.request, 'reCAPTCHA is invalid.')
            return HttpResponseRedirect(self.request.path_info)

