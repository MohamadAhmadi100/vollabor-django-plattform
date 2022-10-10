from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.db.models import Count
from Q_And_A.models import Question, Answer, AnswerLike, AnswerDislike, QuestionAnswerManager
from django.utils.translation import gettext_lazy as _


def questions(request):
    question_list = Question.objects.filter(is_verified=True).annotate(answer_numbers=Count('answer')).order_by('-answer_numbers')
    context = {
        'questions': question_list
    }

    if request.method == 'POST':
        if 'send-question' in request.POST:
            the_question = request.POST.get('posed-question')
            if the_question is None or the_question.strip() == "":
                messages.error(request, 'Question content should not be empty')
            else:
                if not request.user.is_authenticated:
                    full_name = request.POST.get('full-name')
                    if full_name is None or full_name.strip() == "":
                        messages.error(request, _('Full name should not be empty'))
                    else:
                        email = request.POST.get('email')
                        Question(question=the_question, full_name=full_name, email=email).save()
                        messages.success(request, _('Question is submitted successfully. It will be placed on website '
                                                    'within 24 hours.'))
                else:
                    Question(question=the_question, user=request.user).save()
                    messages.success(request, _('Question is submitted successfully. It will be placed on website '
                                                'within 24 hours.'))

        return HttpResponseRedirect(request.path_info)  # redirect to the same page

    return render(request, 'q_and_a_questions.html', context)


def question_and_answers(request, question_id):
    selected_question = Question.objects.get(id=question_id)
    context = {
        'selected_question': selected_question,
        'answers': selected_question.answer_set.filter(is_verified=True).annotate(like_numbers=Count('answerlike')).order_by(
            '-like_numbers'),
    }
    if request.user.is_authenticated:
        context['is_manager'] = QuestionAnswerManager.objects.filter(user=request.user).count()

    if request.method == "POST":
        if 'question-answer' in request.POST:
            answer = request.POST.get('question-answer')
            if request.user.is_authenticated:
                if len(answer.strip()) > 0:
                    Answer(user=request.user, question=selected_question, answer=answer).save()
                    messages.success(request, _("Answer has been submitted successfully. it will be placed on website "
                                                "within 24 hours."))
            else:
                messages.success(request, _("You have to login first"))

        if 'like-answer' in request.POST:
            answer_pk = request.POST.get('like-answer')
            if answer_pk is None:
                return JsonResponse({"success": False, 'error': _('An error is occurred')})
            selected_answer = Answer.objects.get(pk=answer_pk)

            dislike_exists = AnswerDislike.objects.filter(user=request.user, answer=selected_answer).count()
            if dislike_exists:
                return JsonResponse({"success": False, 'error': _("You can't like the answer you already disliked")})

            like_exists = AnswerLike.objects.filter(user=request.user, answer=selected_answer).count()
            if like_exists:
                AnswerLike.objects.filter(user=request.user, answer=selected_answer).delete()
                return JsonResponse({"success": True, 'action': 'withdraw'})
            else:
                AnswerLike(user=request.user, answer=selected_answer).save()
                return JsonResponse({"success": True, 'action': 'request'})

        if 'dislike-answer' in request.POST:
            answer_pk = request.POST.get('dislike-answer')
            if answer_pk is None:
                return JsonResponse({"success": False, 'error': _('An error is occurred')})
            selected_answer = Answer.objects.get(pk=answer_pk)

            like_exists = AnswerLike.objects.filter(user=request.user, answer=selected_answer).count()
            if like_exists:
                return JsonResponse({"success": False, 'error': _("You can't dislike the answer you already liked")})

            dislike_exists = AnswerDislike.objects.filter(user=request.user, answer=selected_answer).count()
            if dislike_exists:
                AnswerDislike.objects.filter(user=request.user, answer=selected_answer).delete()
                return JsonResponse({"success": True, 'action': 'withdraw'})
            else:
                AnswerDislike(user=request.user, answer=selected_answer).save()
                return JsonResponse({"success": True, 'action': 'request'})

        if 'delete-answer' in request.POST:
            if context['is_manager']:
                answer_pk = request.POST.get('delete-answer')
                Answer.objects.get(pk=answer_pk).delete()

        return HttpResponseRedirect(request.path_info)  # redirect to the same page

    return render(request, 'q_and_a_question.html', context)
