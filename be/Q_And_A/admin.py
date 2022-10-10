from django.contrib import admin
from .models import *

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(AnswerLike)
admin.site.register(AnswerDislike)

admin.site.register(QuestionAnswerManager)
