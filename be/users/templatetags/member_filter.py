from django import template

register = template.Library()


@register.filter
def convert_to_list(value):
    """
    Template filter created by me (Soroush Mehraban) to convert string like "first, second" to list ["first", "second"]
    we can use this to convert memberprofile interest which is multiselect field to list.

    usage: members.html templates
    """
    return str(value).split(", ")


@register.filter
def get_name_length(profile):
    return len(profile.user.first_name) + len(profile.user.last_name)
