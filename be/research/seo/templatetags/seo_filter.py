from django import template

from seo.models import RobotsMeta, SEO, TitleAndDescription

register = template.Library()


@register.filter
def without_fa(request_path):
    if '/fa' in request_path:
        return request_path.split("/fa")[1]
    else:
        return request_path


@register.filter
def has_meta_index(given_url):
    return RobotsMeta.objects.filter(url=given_url).count()


@register.filter
def get_meta_index(given_url):
    return RobotsMeta.objects.get(url=given_url)


@register.filter
def has_title_and_description(given_url):
    return TitleAndDescription.objects.filter(url=given_url).count()


@register.filter
def get_title_and_description(given_url):
    return TitleAndDescription.objects.get(url=given_url)


@register.filter
def is_seo(given_user):
    return SEO.objects.filter(user=given_user).count()
