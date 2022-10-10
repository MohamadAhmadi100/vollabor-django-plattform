from .models import Applicant, BannedEmail, LegalApplicant
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
import datetime
import hashlib
from users.models import MemberProfile, LegalProfile
from ivc_project.email_sender import send_new_email
import threading


def remove_from_db(primary_key):
    selected_applicant = Applicant.objects.get(pk=primary_key)
    selected_applicant.delete()


def add_legal_user_to_db(selected_applicant_email):
    selected_applicant = LegalApplicant.objects.get(email=selected_applicant_email)

    applicant_username = f'{selected_applicant.first_name.lower().replace(" ", "_")}_{selected_applicant.last_name.lower().replace(" ", "_")}'
    hash_pattern = f'{applicant_username}@tecvico!!!'.encode('utf-8')
    applicant_password = hashlib.sha256(hash_pattern).hexdigest()[:8]

    if User.objects.filter(email=selected_applicant_email.lower()).count():  # if user already exists(natural user):
        new_user = User.objects.get(email=selected_applicant_email.lower())
    else:
        try:
            new_user = User.objects.create_user(applicant_username, selected_applicant.email.lower(), applicant_password)
        except IntegrityError:  # when username already exists, we create a new one based on timestamp so it's unique
            applicant_username += str(datetime.datetime.now().timestamp()).split('.')[0]
            hash_pattern = f'{applicant_username}@tecvico!!!'.encode('utf-8')
            applicant_password = hashlib.sha256(hash_pattern).hexdigest()[:8]
            new_user = User.objects.create_user(applicant_username, selected_applicant.email.lower(), applicant_password)

    new_user.first_name = selected_applicant.first_name
    new_user.last_name = selected_applicant.last_name
    new_user.save()

    LegalProfile(user=new_user, company_name=selected_applicant.company_name,
                 phone_region=selected_applicant.phone_region, phone=selected_applicant.phone).save()

    email_subject = "You got accepted by Tecvico"

    email_content = f"""Hello, {selected_applicant.first_name}.
Thank you for your application. We are honoured you’re interested to join us.
From now on, you can login to our website (https://www.tecvico.com/login) with your email address and this password:
Email: {selected_applicant.email}
Password: {applicant_password}

Also, You can change your info  whenever you want by going to your Profile after logging in.
    
Regards,
TECVICO Team

	
"""
    # threading.Thread(target=send_new_email, args=(email_subject, email_content, selected_applicant.email)).start()
    send_new_email(email_subject, email_content, selected_applicant.email)

    selected_applicant.delete()


def add_user_to_db(selected_applicant):
    """
        We add applicants based on their position
        they can login and complete their profile
        * for password: we use sha256 algorithm:
          - at first we crate a string with format firstname_lastname@tecvico!!!
          - then we run sha256 algorithm and extract the first 8 characters from hexdigest

    """
    applicant_username = f'{selected_applicant.first_name.lower().replace(" ", "_")}_{selected_applicant.last_name.lower().replace(" ", "_")}'
    hash_pattern = f'{applicant_username}@tecvico!!!'.encode('utf-8')
    applicant_password = hashlib.sha256(hash_pattern).hexdigest()[:8]

    if User.objects.filter(email=selected_applicant.email.lower()).count():  # if user already exists (legal user):
        new_user = User.objects.get(email=selected_applicant.email.lower())
    else:
        try:
            new_user = User.objects.create_user(applicant_username, selected_applicant.email.lower(), applicant_password)
        except IntegrityError:  # when username already exists, we create a new one based on timestamp so it's unique
            applicant_username += str(datetime.datetime.now().timestamp()).split('.')[0]
            hash_pattern = f'{applicant_username}@tecvico!!!'.encode('utf-8')
            applicant_password = hashlib.sha256(hash_pattern).hexdigest()[:8]
            new_user = User.objects.create_user(applicant_username, selected_applicant.email.lower(), applicant_password)

    new_user.first_name = selected_applicant.first_name
    new_user.last_name = selected_applicant.last_name
    new_user.save()

    new_member_profile = MemberProfile(user=new_user, position="Learner", field_of_study=selected_applicant.field_of_study,
                                       degree=selected_applicant.degree, status=selected_applicant.status,
                                       phone=selected_applicant.phone, phone_region=selected_applicant.phone_region,
                                       cv_file=selected_applicant.cv_file,
                                       referred_by=selected_applicant.referred_by,
                                       is_internship=selected_applicant.is_internship)
    new_member_profile.save()

    """
    Now we created that user inside our database, let's inform him with an email:
    """
    email_subject = "You got accepted by Tecvico"
    email_content = f"""Hello, {selected_applicant.first_name}.
Thank you for your application. We are honoured you’re interested to join us.
From now on, you can login to our website (https://www.tecvico.com/login) with your email address and this password:
Email: {selected_applicant.email}
Password: {applicant_password}

Also, You can change your info whenever you want by going to your Profile after logging in.

Regards,
TECVICO Team


"""
    # threading.Thread(target=send_new_email, args=(email_subject, email_content, selected_applicant.email)).start()
    send_new_email(email_subject, email_content, selected_applicant.email)


def accept_applicant(selected_email, selected_position):
    selected_applicant = Applicant.objects.get(email=selected_email)
    selected_user = User.objects.get(email=selected_email)
    selected_member_profile = MemberProfile.objects.get(user=selected_user)

    if selected_member_profile.position != selected_position:
        selected_member_profile.position = selected_position
        selected_member_profile.save()

        email_subject = "You have been promoted"
        email_content = f"""Congratulations!.
You have been promoted from "Learner" to "{selected_position}". We hope to see you on lots of projects.

Regards,
TECVICO Team
"""
        # threading.Thread(target=send_new_email, args=(email_subject, email_content, selected_applicant.email)).start()
        send_new_email(email_subject, email_content, selected_applicant.email)

    selected_applicant.delete()


def reject_applicant(selected_email, reason, applicant_type='natural'):
    if applicant_type == 'natural':
        selected_applicant = Applicant.objects.get(email=selected_email)
    else:
        selected_applicant = LegalApplicant.objects.get(email=selected_email)

    selected_user = User.objects.get(email=selected_email)

    selected_name = selected_applicant.first_name

    selected_applicant.delete()
    selected_user.delete()

    email_subject = "Unfortunately, you're no longer a member of Tecvico"
    email_content = f"""Hello, {selected_name}.
We're sorry to inform you that you are no longer a member of tecvico. Here is the reason stated by Tecvico:

"{reason}"

Regards,
TECVICO Team
"""
    # threading.Thread(target=send_new_email, args=(email_subject, email_content, selected_applicant.email)).start()
    send_new_email(email_subject, email_content, selected_applicant.email)

    BannedEmail(banned_email=selected_email).save()
