from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import datetime


class TaskTracker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_position = models.CharField(max_length=100, null=True)
    title = models.CharField(max_length=30)
    task = models.TextField(blank=True,default="")
    start_time = models.TimeField(null = True)
    end_time = models.TimeField(null = True)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, default="New")
    has_finished = models.BooleanField(default=False)
    suggested_time = models.CharField(max_length=50, null=True)
    start_pause = models.TimeField(null=True)
    end_pause = models.TimeField(null=True)
    def __str__(self):
        return self.title
        
    def get_duration(self):
        if self.start_time != None and self.end_time != None:
            start = datetime.strptime(str(self.start_time), '%H:%M:%S')
            end = datetime.strptime(str(self.end_time), '%H:%M:%S')
            duration = end - start
            if self.start_pause != None and self.end_pause != None:
                start_pause = datetime.strptime(str(self.start_pause), '%H:%M:%S')
                end_pause = datetime.strptime(str(self.end_pause), '%H:%M:%S')
                pause_duration = end_pause - start_pause
                duration = duration - pause_duration
            return duration
        else:
            return "None"
        
    class Meta:
        ordering = ['-date', '-pk']


class ManagerList(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(TaskTracker, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, default="")

    def __str__(self):
        return self.task.title + " by " + self.task.user.first_name + " " + self.task.user.last_name
    
    class Meta:
        ordering = ['-pk']

class AttendanceList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField(default=timezone.now)
    end_time = models.TimeField(null=True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name + " at " + str(self.date)
    class Meta:
        ordering = ['-date', '-pk']

