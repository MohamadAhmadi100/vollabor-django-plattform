# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from stripe import Balance

from dashboard.models import ApplicantManager
from users.models import LegalProfile
from django.utils.translation import gettext_lazy as _
from .forms import ApplicantForm, LegalApplicantForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from ivc_project.recaptcha_validator import is_recaptcha_valid
import secrets
from .applicant_handler import *
import re

import json
import hashlib
from django.contrib.auth import get_user_model
from users.models import MemberProfile
import threading
from django.contrib.auth import  authenticate, login


from .models import LegalApplicant, FieldSuggestion
from .utils import convert_entered_to_given_email

Users=get_user_model()


def is_superuser(user):
    return user.is_authenticated and user.is_superuser


def is_applicant_manager(user):
    if user.is_anonymous:
        return False
    else:
        return ApplicantManager.objects.filter(user=user).count()


def upload_cv(request):
    """
    view which shows join us form
    it gets the form from ApplicantForm which we made in join/forms.py
    """
    form = ApplicantForm()
    legal_form = LegalApplicantForm(auto_id='legal_%s')

    if request.method == 'POST':  # if user clicked join button
        if 'company_name' in request.POST:  # if user submitted a legal form
            legal_form = LegalApplicantForm(request.POST, auto_id='legal_%s')
            if legal_form.is_valid():
                first_name = str(legal_form.cleaned_data.get('first_name'))
                last_name = str(legal_form.cleaned_data.get('last_name'))
                entered_email = legal_form.cleaned_data.get('email')  # actual email address

                given_email = entered_email

                users_with_given_email = User.objects.filter(email=given_email)
                previous_valid_request = LegalApplicant.objects.filter(email=given_email, is_valid=True)

                something_is_wrong = users_with_given_email.count() > 0 or not re.search('[a-zA-Z]', first_name) \
                                     or not re.search('[a-zA-Z]', last_name) or previous_valid_request.count() > 0 \
                                     or BannedEmail.objects.filter(banned_email=given_email).count() > 0

                if something_is_wrong:
                    if users_with_given_email.count() > 0:
                        messages.error(request, "User with given email address already exists")
                    if not re.search('[a-zA-Z]', first_name) or not re.search('[a-zA-Z]', last_name):
                        messages.error(request, "Your name should be entered in English")
                    if BannedEmail.objects.filter(banned_email=given_email).count() > 0:
                        messages.error(request,
                                       "Unfortunately, you are a removed member of tecvico and we are unable to "
                                       "have you")
                    if previous_valid_request.count() > 0:
                        messages.error(request, "You already have submitted a request. Please wait for the response "
                                                "of our team.")
                    return render(request, 'join/upload_cv.html', {'form': form, 'legal_form': legal_form})

                is_valid = is_recaptcha_valid(request)
                if not is_valid:
                    messages.error(request, 'reCAPTCHA is invalid, please try again')
                    return render(request, 'join/upload_cv.html', {'form': form, 'legal_form': legal_form})

                # at first we delete previous invalid requests:
                LegalApplicant.objects.filter(email=given_email, is_valid=False).delete()

                legal_form.save()  # then we save current info

                # for gmail cases and cases when user enters email with Uppercase
                current_applicant = LegalApplicant.objects.get(email=entered_email)
                current_applicant.email = given_email
                current_applicant.save()
                

                # after that, we set a verification token specifically to that user which is a random 8 digit hex
                # value
                generated_token = secrets.token_urlsafe(8)
                current_applicant = LegalApplicant.objects.get(email=given_email)
                current_applicant.phone_region = request.POST['phone_region']
                current_applicant.applicant_token = generated_token
                current_applicant.save()
                add_user_to_db(current_applicant)
                messages.success(request,
                             _('You submitted the application request successfully. An email containing your login credentials has been sent to your email address.'))
                # now we send an email to that user and give him the verification code:
#                 email_subject = "Email Confirmation - Tecvico"
#                 email_content = f"""Hello, {first_name}.
# Your application has been submitted, please confirm this email address by entering verification code to our website:

# VERIFICATION CODE: {generated_token}

# Regards,
# Tecvico Team
#                 """

#                 send_new_email(email_subject, email_content, given_email)
                return redirect('login')

        else:  # if user submitted a natural form:
            form = ApplicantForm(request.POST, request.FILES)
            if form.is_valid():  # if information is valid
                cv_file = form.cleaned_data.get('cv_file')
                first_name = str(form.cleaned_data.get('first_name'))
                last_name = str(form.cleaned_data.get('last_name'))
                entered_email = form.cleaned_data.get('email')  # actual email address

                given_email = convert_entered_to_given_email(entered_email)

                users_with_given_email = User.objects.filter(email=given_email)

                # something_is_wrong = cv_file.content_type != 'application/pdf' \
                #                      or users_with_given_email.count() > 0 \
                #                      or not re.search('[a-zA-Z]', first_name) or not re.search('[a-zA-Z]', last_name) \
                #                      or BannedEmail.objects.filter(banned_email=given_email).count() > 0

                # if something_is_wrong:
                #     if cv_file.content_type != 'application/pdf':  # if cv file format is not PDF
                #         messages.error(request, "You're CV must be in PDF format")
                #     if users_with_given_email.count() > 0:
                #         messages.error(request, "User with given email address already exists")
                #     if not re.search('[a-zA-Z]', first_name) or not re.search('[a-zA-Z]', last_name):
                #         messages.error(request, "Your name should be entered in English")
                #     if BannedEmail.objects.filter(banned_email=given_email).count() > 0:
                #         messages.error(request,
                #                       "Unfortunately, you are a removed member of tecvico and we are unable to "
                #                       "have you")
                #     return render(request, 'join/upload_cv.html', {'form': form, 'legal_form': legal_form})
                if False:
                    pass
                else:
                    # at first we check recaptcha:
                    is_valid = is_recaptcha_valid(request)
                    if not is_valid:
                        messages.error(request, 'reCAPTCHA is invalid, please try again')
                        return render(request, 'join/upload_cv.html', {'form': form, 'legal_form': legal_form})

                    """
                    When user info is correct. we send a confirmation email to that user.
                    so at first there is is_valid attribute in Applicant model which is false by default
                    after confirmation we change it to true, then superusers can see that applicant.
                    """
                    # at first we delete previous invalid requests:
                    Applicant.objects.filter(email=given_email).delete()

                    form.save()  # then we save current info

                    # for gmail cases and cases when user enters email with Uppercase
                    current_applicant = Applicant.objects.get(email=entered_email)
                    current_applicant.phone_region = 'ir'
                    current_applicant.email = given_email
                    current_applicant.save()

                    # after that, we set a verification token specifically to that user which is a random 8 digit hex
                    # value
                    generated_token = secrets.token_urlsafe(8)
                    current_applicant = Applicant.objects.get(email=given_email)
                    current_applicant.phone_region = request.POST['phone_region']
                    current_applicant.applicant_token = generated_token
                    current_applicant.save()
                    add_user_to_db(current_applicant)
                    messages.success(request,
                             _('You submitted the application request successfully. An email containing your login credentials has been sent to your email address.'))
                    
                    # now we send an email to that user and give him the verification code:
#                     email_subject = "Email Confirmation - Tecvico"
#                     email_content = f"""Hello, {first_name}.
# Your application has been submitted, please confirm this email address by entering verification code to our website:

# VERIFICATION CODE: {generated_token}

# Regards,
# Tecvico Team
#                 """
#                     send_new_email(email_subject, email_content, given_email)

                    # at the end, we save suggested field if exists
                    # if 'field_suggestion' in request.POST:
                    #     FieldSuggestion(suggested_field=request.POST['field_suggestion'], suggested_by=given_email) \
                    #         .save()
                    #     threading.Thread(target=send_new_email,
                    #                      args=("New Field suggestion",
                    #                            f"{request.POST['field_suggestion']} - {given_email}",
                    #                            'smehraban2013@gmail.com')).start()

                    return redirect('login')

    return render(request, 'join/upload_cv.html', {'form': form, 'legal_form': legal_form})


def activation_email(request, applicant_email):
    current_applicants = Applicant.objects.filter(email=applicant_email)  # get applicant by email filter which is 0

    # or 1
    if current_applicants.count() == 0:  # if result is zero, then we don't have any applicant with that email
        return redirect('/not-found-404')

    current_applicant = current_applicants[0]  # else we just have one applicant, since it's unique and we excluded
    # previous requests in upload_cv view

    # if it's more than 30 minutes that user requested application, then we remove and he should send it again
    if current_applicant.created_time < timezone.now() - datetime.timedelta(minutes=30):
        Applicant.objects.filter(email=applicant_email).delete()
        return redirect('/not-found-404')

    if request.POST:
        # at first we check recaptcha:
        is_valid = is_recaptcha_valid(request)
        if not is_valid:
            messages.error(request, 'reCAPTCHA is invalid, please try again')
            return HttpResponseRedirect(request.path_info)  # redirect to the same page`

        if request.POST['verification_code'] == current_applicant.applicant_token:
            """
            At first, we save applicant as a valid applicant so that superusers are able to modify
            their position (By default they should be learner and after accepting the position, the applicant
            will be removed).
            """
            current_applicant.is_valid = True
            current_applicant.save()

            add_user_to_db(current_applicant)

            messages.success(request,
                             _('You submitted the application request successfully. An email containing your login credentials has been sent to your email address.'))
            return redirect('login')
        else:
            messages.error(request, "Verification code is wrong, please try again")
            return HttpResponseRedirect(request.path_info)
    return render(request, 'join/acc_active_email.html')


def legal_activation_email(request, applicant_email):
    current_applicants = LegalApplicant.objects.filter(email=applicant_email)  # get applicant by email filter which
    # is 0 or 1
    if current_applicants.count() == 0:  # if result is zero, then we don't have any applicant with that email
        return redirect('/not-found-404')

    current_applicant = current_applicants[0]  # else we just have one applicant, since it's unique and we excluded
    # previous requests in upload_cv view

    if current_applicant.is_valid:  # for valid users we don't accept confirmation emails anymore
        return redirect('/not-found-404')
    # if it's more than 30 minutes that user requested application, then we remove and he should send it again
    elif current_applicant.created_time < timezone.now() - datetime.timedelta(minutes=30):
        LegalApplicant.objects.filter(email=applicant_email).delete()
        return redirect('/not-found-404')

    if request.POST:
        # at first we check recaptcha:
        is_valid = is_recaptcha_valid(request)
        if not is_valid:
            messages.error(request, 'reCAPTCHA is invalid, please try again')
            form = ApplicantForm()
            legal_form = LegalApplicantForm()
            return render(request, 'join/upload_cv.html', {'form': form, 'legal_form': legal_form})

        if request.POST['verification_code'] == current_applicant.applicant_token:
            """
            At first, we save applicant as a valid applicant so that superusers are able to modify
            their position (By default they should be learner and after accepting the position, the applicant
            will be removed).
            """
            current_applicant.is_valid = True
            current_applicant.save()

            return render(request, 'join/after_verification.html')
        else:
            messages.error(request, "Verification code is wrong, please try again")
            return HttpResponseRedirect(request.path_info)
    return render(request, 'join/acc_active_email.html')


@user_passes_test(is_applicant_manager)
def cv_list(request):
    """
    Only superusers can see applicant requests
    """
    if request.method == "POST":  # if user wants to accept or reject applicant
        try:  # accept
            data_accept_email = request.POST['data-accept-email']
            selected_position = request.POST['selected-position']
            applicant_type = request.POST['applicant-type']
            if applicant_type == 'natural':
                accept_applicant(data_accept_email, selected_position)
            if applicant_type == 'legal':
                add_legal_user_to_db(data_accept_email)

        except KeyError:  # reject
            data_reject_email = request.POST['data-reject-email']
            reject_reason = request.POST['reject-reason']
            applicant_type = request.POST['applicant-type']
            if applicant_type == 'legal' or applicant_type == 'natural':
                reject_applicant(data_reject_email, reject_reason, applicant_type)

        return HttpResponseRedirect(request.path_info)  # redirect to the same page

    applicants = Applicant.objects.all()
    legal_applicants = LegalApplicant.objects.all()
    return render(request, 'join/cv_list.html', {'applicants': applicants, 'legal_applicants': legal_applicants})




# ............................................................................

def simple_register(request):
    next=request.GET.get('next')
    template_name='join/simple_register.html'
    if request.method=='POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        phone_region=request.POST.get('phone_region')
        user=Users.objects.filter(email=email).first()
        if user is None:
            user_pass = str(datetime.datetime.now().timestamp()).split('.')[0]
            hash_pattern = f'{user_pass}@tecvico!!!'.encode('utf-8')
            password = hashlib.sha256(hash_pattern).hexdigest()[:8]
            if '@gmail.com' in email:  # in case email is gmail, soroushmehraban and soroush.mehraban should be
                # the same
                gmail_username = email.split("@gmail.com")[0]
                gmail_username_sections = gmail_username.split(".")
                gmail_username = "".join(gmail_username_sections)
                email = f"{gmail_username}@gmail.com"


            new_user=Users.objects.create_user(email,email,password)
            new_user.first_name=first_name
            new_user.last_name=last_name
            new_user.is_active=True
            new_user.save()
            new_member_profile = MemberProfile.objects.create(user=new_user, position="Learner",balance=0,phone=phone,phone_region=phone_region)
            """
            Now we created that user inside our database, let's inform him with an email:
            """
            email_subject = "You got accepted by Tecvico"
            email_content = f"""Hello, {first_name}.
            Thank you for your application. We are honoured you’re interested to join us.
            From now on, you can login to our website (https://www.tecvico.com/login) with your email address and this password:
            Email: {email}
            Password: {password}

            Also, You can change your info whenever you want by going to your Profile after logging in.

            Regards,
            TECVICO Team

            	
            """
            # threading.Thread(target=send_new_email, args=(email_subject, email_content,email)).start()
            send_new_email(email_subject, email_content,email)
            messages.success(request,'Your password has been sent to your email ')
            # return redirect('simple_register')        

        else:
            messages.error(request,'This email already exist')
            # return redirect('simple_register')        
    context={
        'next':next
    }

    return render (request,template_name,context)



def simple_login(request):
    if request.method=='POST':
        is_valid = is_recaptcha_valid(request)
        if is_valid:
            username=request.POST.get('username')
            password=request.POST.get('password')
            next=request.POST.get('next')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if  next == 'None':
                    return redirect('/dashboard')               
                else:
                    return redirect(next)
            else:
                messages.error(request, 'This email does not exist')
                return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'reCAPTCHA is invalid, please try again')
            return redirect(request.META.get('HTTP_REFERER'))
