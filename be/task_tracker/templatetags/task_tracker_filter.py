import math

from django import template

register = template.Library()


@register.filter
def format_time(time):
    return "{:02d}:{:02d}:{:02d}".format(get_hour_part(time), get_minute_part(time), get_second_part(time))


@register.filter
def format_time_part(time):
    return "{:02d}".format(time)


@register.filter
def get_hour_part(time):
    return math.floor(time / 3600)


@register.filter
def get_minute_part(time):
    hour_part = get_hour_part(time)
    remaining_time = time - 3600 * hour_part
    return math.floor(remaining_time / 60)


@register.filter
def get_second_part(time):
    hour_part = get_hour_part(time)
    minute_part = get_minute_part(time)
    return time - 3600 * hour_part - 60 * minute_part
