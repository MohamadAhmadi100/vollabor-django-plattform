from django import template

from industrial_manager.models import IndustrialManager

register = template.Library()


@register.filter
def is_industrial_manager(given_user):
    return IndustrialManager.objects.filter(user=given_user).count()
