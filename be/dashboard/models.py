from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from ivc_website.models import Project, IndustrialArea, ProjectArea, ProjectSupervisor, ProjectProposal, \
    project_type_choices

week_days = (
    ("Monday", 'Monday'),
    ("Tuesday", 'Tuesday'),
    ("Wednesday", 'Wednesday'),
    ("Thursday", 'Thursday'),
    ("Friday", 'Friday'),
    ("Saturday", 'Saturday'),
    ("Sunday", 'Sunday'),
)

item_types = (
    ('Mandatory', 'Mandatory'),
    ('Optional', 'Optional'),
)

from_items = (
    ('Tecvico', 'Tecvico'),
    ('Company', 'Company'),
)


class CompanyCollaboration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default="Not Determined")
    section = models.CharField(max_length=100, default="Not Determined")
    content = models.TextField()
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} - {self.content}"


class ProjectRating(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    collaborator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rating_collaborator", null=True)
    rating = models.IntegerField(default=0)
    reviewer = models.ForeignKey(User, related_name="rating_reviewer", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.project} - {self.collaborator} -> {self.rating}'


class Announcement(models.Model):
    """
    Announcement: every mentor on dashboard can send announcements and others can see that
    - title: title of the announcement. it should be unique because in dashboard/view we have to get the title and
    then assign a owner to it (#TODO if you have better idea)
    - description: a description about the announcement
    - owner: owner of announcement
    """
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    creation_time = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.title


class AnnouncementView(models.Model):
    """
    Announcement View: determines whether a person has viewed an announcement or not
    """
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.announcement} - {self.user}"


class Notification(models.Model):
    """
    This models helps everyone to see notification
    - title: title of a notification, it's a bold text on the beginning
    - description: description of a notification
    - target: the person whom the notification belongs to
    - link: link to open when user click that notification
    - seen: determines that target user has seen the notification or not
    - date: date to show when the notification is created. we show this in format like 5 minutes ago with the help of
     django.contrib.humanize
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    target = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    link = models.CharField(max_length=100, default="")
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title}: {self.description}"

    class Meta:
        ordering = ['-date']


class WeeklyMeetingTime(models.Model):
    """
    Times which is set for meeting of a project
    this is actually a row on a project weekly meeting table demonstrating a time
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    weekly_meeting_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-weekly_meeting_time']

    def __str__(self):
        return f"{self.project} - {self.weekly_meeting_time}"


class WeeklyMeetingAttendee(models.Model):
    """
    This model helps to record attendees of a weekly meeting
    """
    weekly_meeting = models.ForeignKey(WeeklyMeetingTime, on_delete=models.CASCADE)
    attendee = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    acceptable_absence = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.weekly_meeting} - {self.attendee}"


class UserEmail(models.Model):
    email_subject = models.CharField(max_length=400)
    email_content = models.TextField()
    sender = models.ForeignKey(User, related_name="email_sender", on_delete=models.CASCADE, null=True, blank=False)
    receiver = models.ForeignKey(User, related_name="email_receiver", on_delete=models.CASCADE, null=True, blank=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"From: {self.sender} to {self.receiver}"


class UnSubscriber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class ContractItem(models.Model):
    item = models.TextField()
    item_type = models.CharField(max_length=50, choices=item_types, default="Mandatory")
    pub_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.item} - {self.item_type}"

    class Meta:
        ordering = ['item_type', 'pub_date']


class ProjectContractItem(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    item = models.TextField()
    item_type = models.CharField(max_length=50, choices=item_types, default="Mandatory")
    agree = models.BooleanField(null=True)
    disagree = models.BooleanField(null=True)
    disagreement_reason = models.TextField(null=True, blank=True)
    from_item = models.CharField(max_length=50, choices=from_items, default="Tecvico")
    pub_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.project} - {self.item} - {self.item_type}"

    class Meta:
        ordering = ['item_type', 'pub_date']


class ExpertAreaItem(models.Model):
    item = models.TextField()

    def __str__(self):
        return f'{self.item}'


class ProjectExpertAreaItem(models.Model):
    project_area = models.ForeignKey(ProjectArea, on_delete=models.CASCADE, null=True, blank=False)
    item = models.TextField()
    agree = models.BooleanField(null=True)

    def __str__(self):
        return f'{self.project_area} - {self.item}'


class ApplicantManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Reviewer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class ProposalOpinionItem(models.Model):
    """
    Items that reviewers should score on each proposal that is submitted.
    the content of each item from this table loads dynamically to ProposalOpinion table once a project is created
    """
    item = models.TextField()
    project_type = models.CharField(max_length=12, choices=project_type_choices, default='Research')

    def __str__(self):
        return f"{self.item}"

    class Meta:
        ordering = ['pk']


class ProposalOpinion(models.Model):
    """
    - proposal: since on_delete is models.CASCADE, after deleting the proposal all the rows related to that are deleted

    - item: items that we define on ProposalOpinionItem table. since there is a probability that one day we decide to
    remove one item, I decide to put TextField instead of ForeignKey and let the item remains for previous proposals

    - reviewer: the reviewer who scores the item of the proposal. after deleting the reviewer from the project all of his
    opinions will disappear

    - score: an score which a positive integer
    """
    proposal = models.ForeignKey(ProjectProposal, on_delete=models.CASCADE)
    item = models.ForeignKey(ProposalOpinionItem, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.proposal} | Reviewer: {self.reviewer} | score: {self.score}"

    class Meta:
        ordering = ['pk']


class ProposalComment(models.Model):
    proposal = models.ForeignKey(ProjectProposal, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return f"{self.proposal} - {self.reviewer}"
        
        
class AdFormWS(models.Model):
    title = models.CharField(max_length=100, default="")
    date = models.DateField(default=timezone.now)
    time_to_start = models.TimeField(default=timezone.now)
    duration = models.TimeField(default=timezone.now)
    speaker = models.CharField(max_length=150, null=True)
    suggest_country = models.CharField(max_length=150, null=True)
    email = models.EmailField(default="", null= True)
    phone_number = models.CharField(default="", max_length=15, null= True)
    keyword = models.CharField(max_length=100, null=True)
    skills = models.CharField(max_length=100, null=True)
    image = models.ImageField(upload_to="dashboard/", null= True)
    price = models.IntegerField(default=0)
    description = models.TextField(max_length=150, blank=True,)
    address = models.TextField(max_length=150, blank=True,)

    def __str__(self):
        return self.title
