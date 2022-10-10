from django.shortcuts import render
from .course_query import get_courses
from .models import ScheduleCourse
import itertools


def courses(request):
    """
    Course view:
    at first it gets all of the courses and then we divide it by their subject
    """
    schedule_courses, archive_courses = get_courses()

    context = {
        'schedule_courses': schedule_courses,
        'archive_courses': archive_courses
    }

    return render(request, 'courses/courses.html', context)


def course_item(request, course_id):
    current_course = ScheduleCourse.objects.get(pk=course_id)

    context = {
        'course': current_course,
    }
    return render(request, 'courses/course_item.html', context)
