from django import template

from collaborate_with_us.models import StaffManager

register = template.Library()


@register.filter
def is_staff_manager(given_user):
    return StaffManager.objects.filter(user=given_user).count()
