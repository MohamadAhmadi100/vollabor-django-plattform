from django.db import models

subject_choices = (
    ("Schedules", 'Schedules'),
    ("Archives", "Archives")
)


class Course(models.Model):
    """
    Course schema: Model to describe each course

    -image: image of tutorial we show on course card
    -title: title of the tutorial (100 letters max)
    -description: a short description about the tutorial
    -youtube_url: (!Important): the link should be embed url which we can extract from youtube iframe
    """
    image = models.ImageField(upload_to='courses/images/', default='course_default.jpg')
    title = models.CharField(max_length=100)
    description = models.TextField()
    youtube_url = models.URLField(blank=False, null=False)

    def __str__(self):
        return self.title


class ScheduleCourse(models.Model):
    """
    Schedule course: Courses that we're going to teach in future
    - title: title of that course
    - description: description of that course
    - time: time when course is going to be started
    """
    title = models.CharField(max_length=100)
    description = models.TextField()
    time = models.DateField(null=False, blank=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-time']


class CourseItem(models.Model):
    """
    items provided in each courses, useful when we're going to show them in nested list
    """
    related_course = models.ForeignKey(ScheduleCourse, on_delete=models.CASCADE, null=True, blank=True)
    item_name = models.CharField(max_length=100)
    item_parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.item_name} - {self.related_course}"
