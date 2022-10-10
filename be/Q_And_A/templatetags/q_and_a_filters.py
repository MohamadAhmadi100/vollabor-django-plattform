from django import template

from Q_And_A.models import AnswerLike, AnswerDislike

register = template.Library()


@register.filter
def has_liked(user, answer):
    if user.is_authenticated:
        return AnswerLike.objects.filter(answer=answer, user=user).count()
    else:
        return False


@register.filter
def has_disliked(user, answer):
    if user.is_authenticated:
        return AnswerDislike.objects.filter(answer=answer, user=user).count()
    else:
        return False
