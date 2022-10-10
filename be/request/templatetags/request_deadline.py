from django import template
from datetime import datetime, timedelta
register = template.Library()


# def deadline(created):
# 	return{
# 	'created': created + timedelta(days=100),
# 	}
@register.inclusion_tag('request/reviewer-page.html')
def deadline():
    return "salmmmmm"