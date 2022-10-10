from django.shortcuts import render
from seo.models import UserFootprint
from FAQ.models import FAQ


def frequently_asked_question_view(request):
    if request.user.is_authenticated:
        create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)
    return render(request, 'FAQ/FAQ.html', context={
        'question_answers': FAQ.objects.all()
    })
