from django import template
from forum.models import *
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def count_comment_topic(id_topic):
	obj_topic = Postes.objects.get(id=id_topic)

	comments = TopicComment.objects.filter(topic=obj_topic).count()
	reply_comments = ReplyComment.objects.filter(topic=obj_topic).count()

	return comments + reply_comments


@register.simple_tag
def topic_count(id_maincategory):
	obj_maincategory = MainCategory.objects.get(id=id_maincategory)

	count = 0
	for i in obj_maincategory.childern.Active():
		for t in i.postes.Published():
			count += 1

	return count
