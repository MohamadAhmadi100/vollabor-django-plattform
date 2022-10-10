from .models import Course, ScheduleCourse


def get_courses():
    archive_set = Course.objects.all()  # all archive courses
    schedule_set = ScheduleCourse.objects.all()  # all schedule courses

    archive_courses = []
    archive_index = 0

    """
       we have inner list for each list
       the inner list contains 3 objects at max which is the number of cards we show on a row 
   """
    for archive in archive_set:
        if archive_index % 3 == 0:
            archive_courses.append([])  # append new row
        archive_courses[-1].append(archive)
        archive_index += 1

    return schedule_set, archive_courses
