from django.db import models
from django.contrib.auth.models import User
from  django.utils import timezone
from django.utils.translation import gettext_lazy as _


# Create your models here.

class MainField(models.Model):
    title = models.CharField(max_length=100, default=None)
    user_add = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

class SubField(models.Model):
    parent=models.ForeignKey(MainField,on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default=None)
    user_add = models.BooleanField(default=False)


    def __str__(self):
        return self.title


class VirtualEvent(models.Model):
    status=(
        ('Create','Create'),
        ('Reject','Reject'),
        ('Revise','Revise'),
        ('Remove','Remove'),
        ('Select_expert','Select_expert'),
        ('Expert_decide','expert_decide'),
        ('Resubmit_to_expert','Resubmit_to_expert'),
        ('Resubmit_to_director','Resubmit_to_director'),
        ('Published','Published'),
    )
    type=models.CharField(max_length=30)
    unique_id = models.CharField(max_length=30)
    top_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'presenter')
    title = models.CharField(max_length=1000)
    start_date = models.DateField(null=True,blank=True)
    price = models.IntegerField(null=True)
    duration = models.CharField(max_length=50, default=0)
    main_field = models.ManyToManyField(MainField)
    sub_field = models.ManyToManyField(SubField)
    status = models.CharField(max_length=30,choices=status, default="Create")
    created = models.DateTimeField(auto_now_add=True)
    expert=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    contract=models.FileField(upload_to='',null=True)
    sign=models.TextField(max_length=50000,null=True)


    def __str__(self):
        return self.title



class Seminar(models.Model):
    unique_id = models.CharField(max_length=30,null=True)
    image = models.ImageField(upload_to="Seminar/")
    description = models.TextField(max_length=5000)
    language = models.CharField(max_length=1000, null=True)
    speaker = models.CharField(max_length=1000, null=True)
    keyword = models.CharField(max_length=1000, null=True,blank=True)
    skills = models.CharField(max_length=1000, null=True,blank=True)
    video = models.CharField(max_length=200, null=True, default="")
    time_zone = models.CharField(max_length=1000, default="", null=True)

class Course(models.Model):
    unique_id = models.CharField(max_length=30,null=True)
    image = models.ImageField(upload_to="Course/")
    description = models.TextField(max_length=5000)
    language = models.CharField(max_length=1000, null=True)
    speaker = models.CharField(max_length=1000, null=True)
    keyword = models.CharField(max_length=1000, null=True,blank=True)
    skills = models.CharField(max_length=1000, null=True,blank=True)
    video = models.CharField(max_length=200, null=True, default="")
    time_zone = models.CharField(max_length=1000, default="", null=True)


class Workshop(models.Model):
    unique_id = models.CharField(max_length=30,null=True)
    image = models.ImageField(upload_to="workshop/")
    description = models.TextField(max_length=5000)
    language = models.CharField(max_length=1000, null=True)
    speaker = models.CharField(max_length=1000, null=True)
    keyword = models.CharField(max_length=1000, null=True,blank=True)
    skills = models.CharField(max_length=1000, null=True,blank=True)
    video = models.CharField(max_length=200, null=True, default="")
    time_zone = models.CharField(max_length=1000, default="", null=True)




class Timetable(models.Model):
    vitual_event = models.ForeignKey(VirtualEvent, on_delete=models.CASCADE)
    title=models.CharField(max_length=50,null=True)
    start_date=models.DateField(null=True)
    start_time=models.CharField(max_length=50,null=True)
    end_time=models.CharField(max_length=50,null=True)
    duration=models.CharField(max_length=50,null=True)
    price=models.IntegerField(null=True)
    video_link=models.CharField(max_length=200,null=True)
    document=models.FileField(null=True, upload_to="virtualevent/", max_length=500)  # pdf & powerpoint


class VirtualEventTracking(models.Model):
    position_value=(
            ('expert','expert'),
            ('director','director'),
            ('presenter','presenter'),
        )

    class description(models.TextChoices):
        Create =_('A new virtual event was saved and must be submitted')
        Reject =_('Rejected')
        Revise =_('Revised')
        Remove =_('Deleted')
        Select_expert =_('A new virtual event was submitted')
        Expert_decide =_('The manager selected an expert')
        Resubmit_to_expert =_('The presenter resubmitted the virtual event')
        Resubmit_to_director =_('The presenter resubmited the virtual event')
        Published =_('Accepted and published')
        

    position=models.CharField(max_length=50,choices=position_value,default='supervisor')
    status=models.CharField(max_length=100,null=True,default='create_workshop')
    desc=models.TextField(max_length=1000,choices=description.choices,default=description.Create)
    created=models.DateTimeField(auto_now_add=True)
    vitual_event = models.ForeignKey(VirtualEvent, on_delete=models.CASCADE)
    is_done=models.BooleanField(default=False)
    comment=models.TextField(max_length=2000,null=True,blank=False)


class VirtualEventMemebers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    virtual_event = models.ForeignKey(VirtualEvent, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    section=models.CharField(max_length=50,default='All',blank=True)
    certificate=models.FileField(upload_to="virtualevent/certificates/",blank=True,null=True,default=None)





class EditRequest(models.Model):
    virtual_event=models.ForeignKey(VirtualEvent,on_delete=models.CASCADE)
    reason=models.TextField(max_length=3000,null=True)
    comment=models.TextField(max_length=3000,null=True)
    created=models.DateTimeField(auto_now_add=True)
    to_director=models.BooleanField(default=False)
    is_accept=models.BooleanField(default=False)
    rejected=models.BooleanField(default=False)
    document=models.FileField(blank=True,null=True)

class EditTimetableRequest(models.Model):
    start_date=models.DateField()
    start_time=models.TimeField()
    end_time=models.TimeField()
    editrequest=models.ForeignKey(EditRequest,on_delete=models.CASCADE,null=True)
    time_table=models.ForeignKey(Timetable,on_delete=models.CASCADE,null=True)


