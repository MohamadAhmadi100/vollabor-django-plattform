from django import template
from users.models import Role

register = template.Library()

@register.filter
def is_request_expert(user):
    user_role = Role.objects.filter(user = user)
    position = []
    for role in user_role:
        position.append(role.position)
    if 'workshop expert' in position:
        return True
    else:
        return False

@register.filter
def is_interviewer(user):
    user_role = Role.objects.filter(user = user)
    position = []
    for role in user_role:
        position.append(role.position)
    if 'Interviewer' in position:
        return True
    else:
        return False


@register.filter
def is_reviewer(user):
    user_role = Role.objects.filter(user = user)
    position = []
    for role in user_role:
        position.append(role.position)
    if 'Reviewer' in position:
        return True
    else:
        return False


@register.filter
def is_manager(user):
    user_role = Role.objects.filter(user = user)
    position = []
    for role in user_role:
        position.append(role.position)
    if 'Request manager' in position:
        return True
    else:
        return False