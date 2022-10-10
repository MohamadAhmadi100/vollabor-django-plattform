from users.models import MemberProfile
from .param import *
from math import ceil


def get_user_email_and_phone(request):
    user_email = request.user.email
    if MemberProfile.objects.filter(user=request.user).count() == 1:
        user_phone = request.user.memberprofile.phone
    else:
        user_phone = request.user.legalprofile.phone
    return user_email, user_phone


def get_project_required_responsibility_fee(project_value, position, n_learner=0):
    project_value = float(project_value)
    if position == 'Supervisor':
        dollar_value = shrink_value * project_value * supervisor_share * supervisor_importance_value
    elif position == 'Mentor':
        dollar_value = shrink_value * project_value * mentor_share * mentor_importance_value
    elif position == 'Member':
        dollar_value = shrink_value * project_value * member_share * member_importance_value
    elif position == 'Learner':
        if n_learner == 0:
            return 0
        dollar_value = shrink_value * project_value * learner_share * learner_importance_value
    else:
        return -1

    coin_value = ceil(dollar_value / responsibility_fee_value)
    return coin_value


def increase_user_balance(project, user, position):
    learner_numbers = project.projectlearner_set.filter(state="Collaborator").count()
    required_fee = get_project_required_responsibility_fee(project.project_value, position, learner_numbers)

    user.memberprofile.balance += required_fee
    user.memberprofile.save()


def decrease_user_balance(project, user, position):
    learner_numbers = project.projectlearner_set.filter(state="Collaborator").count()
    required_fee = get_project_required_responsibility_fee(project.project_value, position, learner_numbers)

    user.memberprofile.balance -= required_fee
    user.memberprofile.save()
