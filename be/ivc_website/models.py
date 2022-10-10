#from typing import final
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.utils import timezone
import datetime
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField

project_position_choices = (
    (_("New"), 'New'),
    (_("Pending"), 'Pending'),
    (_("Ongoing"), 'Ongoing'),
    (_("On Hold"), "On Hold"),
    (_("Done"), "Done"),
    (_("Deleted"), "Deleted"),
    (_("Rejected"), "Rejected"),
    (_("Waiting For Signature"), "Waiting For Signature"),
    (_("Inspecting"), "Inspecting"),
    (_("Inspecting Signature"), "Inspecting Signature"),
)

week_days = (
    ("Monday", 'Monday'),
    ("Tuesday", 'Tuesday'),
    ("Wednesday", 'Wednesday'),
    ("Thursday", 'Thursday'),
    ("Friday", 'Friday'),
    ("Saturday", 'Saturday'),
    ("Sunday", 'Sunday'),
)

project_area_opinion_actions = [
    ('accept', 'accept'),
    ('reject', 'reject'),
    ('add', 'add'),
    ('remove', 'remove'),
]

project_area_actions = [
    ('add', 'add'),
    ('remove', 'remove'),
]

project_type_choices = (
    ('Industrial', 'Industrial'),
    ('Research', 'Research'),
    ('Competition', 'Competition'),
)

collaborator_states = (
    ('Pending', 'Pending'),
    ('Accepted Pending', 'Accepted Pending'),
    ('Waiting for Technical Manager Acceptance', 'Waiting for Technical Manager Acceptance'),
    ('Waiting for Research Director Acceptance', 'Waiting for Research Director Acceptance'),
    ('Waiting For Acceptance', 'Waiting For Acceptance'),
    ('Waiting For Signature', 'Waiting For Signature'),
    ('Inspecting Signature', 'Inspecting Signature'),
    ('Idle', 'Idle'),
    ('Collaborator', 'Collaborator'),
)

contract_choices = (
    ('Collaborator', 'Collaborator'),
    ('Ownership', 'Ownership'),
)

project_classes = (
    ('Golden', 'Golden'),
    ('Silver', 'Silver'),
    ('Bronze', 'Bronze'),
    ('Normal', 'Normal'),
)


class Project(models.Model):
    """
    Project Schema:
    - title: Title of the project.
    - project_type: one of the following types:
    -------------- Research
    -------------- Industrial
    -------------- Competition
    - status: it has three status: 1. New 2. Ongoing 3. On Hold 4. Done | owner can choose between each of these
    - is_urgent: if true then with an urgent label it is going to be shown first
    - start date: the date when project started
    - end date: estimated date for project
    - date_added: the date that the project has added to website
    - abstract, support and requirements: descriptions of the project
    - conference_url: Conference URL in case when anyone wants to see the whole conference paper (optional)
    - journal_url: Journal URL in case when anyone wants to see the whole journal paper (optional)
    - code_url: Code URL in case when anyone wants to see the codes (optional)
    - is_valid: by default it's false, After becoming true, other can see this project
    - owner: a person who owns a project
    - main_supervisor: the one who manages all
    - agent: someone who gives the main supervisor information about the project
    - agent_permission: by default it's false, when it's true agent is allowed to change weekly meeting and project link

    - slack_workspace_address, slack_channel_address : slack link of the project
    - google_drive_address: google drive link of the project
    - skype_address: skype link of the project (only collaborators have access)
    - supervisor_message: the message that supervisor sends on the email of slack

    - weekly_day: the day of a week which is set in order to hold the meeting
    - meeting_time: time of the day when meeting is going to be hold.
    - meeting_timezone: e.g. Tehran
    - meeting_language: e.g. Farsi
    - meeting_link: the link that collaborators should go to meet others
    """
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    project_type = models.CharField(max_length=12, choices=project_type_choices, default='Research')
    status = models.CharField(max_length=30, choices=project_position_choices, default='Inspecting',
                              verbose_name=_("Status"))
    is_urgent = models.BooleanField(default=False)
    start_date = models.DateField(verbose_name=_("Start Date"), null=True, blank=True)
    end_date = models.DateField(verbose_name=_("End Date"), null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    description = models.TextField(verbose_name=_("Description"), null=False, default="")
    project_equipment = models.TextField(verbose_name=_("Project Equipment"), null=True, blank=True)
    project_requirements = models.TextField(verbose_name=_("Project Requirements"), null=True, blank=True)
    conference_url = models.URLField(blank=True, null=True, verbose_name=_("Conference URL"))
    journal_url = models.URLField(blank=True, null=True, verbose_name=_("Journal URL"))
    code_url = models.URLField(blank=True, null=True, verbose_name=_("Code URL"))
    is_valid = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name="%(class)s_related_owner",
                              verbose_name=_("Requester"))
    main_supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name="project_main_supervisor", )
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name="%(class)s_related_agent")
    agent_permission = models.BooleanField(default=False)

    # For after submitting Social Form
    slack_workspace_address = models.URLField(null=True, blank=True)
    slack_channel_address = models.URLField(null=True, blank=True)
    google_drive_address = models.URLField(null=True, blank=True)
    skype_address = models.URLField(null=True, blank=True)
    supervisor_message = models.TextField(help_text="It's "
                                                    "optional", null=True, blank=True)

    # For meeting
    week_day = models.CharField(max_length=15, choices=week_days, null=True, blank=True)
    meeting_time = models.TimeField(null=True, blank=True)
    meeting_timezone = models.CharField(null=True, blank=True, max_length=200)
    meeting_link = models.URLField(null=True, blank=True)
    meeting_language = models.CharField(max_length=50, null=False, default='Farsi')

    # for industrial
    project_information = models.FileField(null=True, blank=True, upload_to='project_information/',
                                           verbose_name="Project Information (Optional)")
    reject_reason = models.TextField(null=True, blank=True)
    expert = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name="project_expert")
    expert_is_accepted = models.BooleanField(default=False)
    step = models.IntegerField(default=0)

    fund = models.DecimalField(max_digits=11, decimal_places=2, default=0.0)

    # For Research
    project_class = models.CharField(choices=project_classes, default='Normal', max_length=6)
    final_comment = models.TextField(null=True, blank=True)
    project_value = models.DecimalField(max_digits=11, decimal_places=2, default=0.0)
    project_rfp = models.FileField(null=True, blank=False, upload_to='project_RFP/',
                                   verbose_name='RFP (Request For Proposal)')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = ['-date_added']


class IndustrialArea(models.Model):
    """
    This model determines what areas do we have in general for industrial projects
    """
    area = models.CharField(max_length=200)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.area}"

    class Meta:
        ordering = ['area']


class ProjectArea(models.Model):
    """
    expert: the expert who approves this area to be doable

    --- WHEN CORRESPONDING EXPERT WANTS TO REMOVE OR ADD AN AREA:
        is_confirmed: it is false if technical manager has not responded yet and true if he does
        action: it's either "add" or "remove"
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    area = models.ForeignKey(IndustrialArea, on_delete=models.CASCADE)
    expert = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    # CORRESPONDING EXPERT
    is_confirmed = models.BooleanField(default=True)
    action = models.CharField(choices=project_area_actions, max_length=6, null=True, blank=True)

    def __str__(self):
        return f"{self.project} - {self.area}"


class ProjectAreaOpinion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    area = models.CharField(max_length=200, null=True, blank=False)
    action = models.CharField(max_length=50, choices=project_area_opinion_actions, null=True, blank=False)
    reason = models.TextField()
    opinion_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.project} - {self.area} : {self.action}"

    class Meta:
        ordering = ['-opinion_date']


class AreaReason(models.Model):
    """
    A couple of reasons that tecvico superusers assign on database. when technical manager or project expert wants to
    accept/reject/add/remove and area from a project, he can select reason(s) from the reasons that we assign in here.
    """
    reason = models.TextField()
    type = models.CharField(max_length=50, choices=project_area_opinion_actions, null=True, blank=False)

    def __str__(self):
        return f"{self.type}: {self.reason}"


class ProjectContract(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    contract_type = models.CharField(max_length=15, choices=contract_choices, default='Collaborator')
    contract_file = models.FileField(help_text='It should be in PDF format', upload_to='contracts/',
                                     default="Contract.pdf")
    date_created = models.DateTimeField(default=timezone.now)
    reply_has_been_sent = models.BooleanField(default=False)
    valid = models.BooleanField(default=True)  # False scenario: Project collaborator adds someone to a project and
    # he has not accepted yet

    # for ownership contract
    ready_to_be_printed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.project.title} - {self.user}"


class ProjectContractReply(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    contract_file = models.FileField(help_text='It should be in PDF format', upload_to='contracts/')
    contract_type = models.CharField(max_length=15, choices=contract_choices, default='Collaborator')

    def __str__(self):
        return f"{self.project.title} - {self.user}"


class ProjectSupervisor(models.Model):
    """
    Other than main supervisors, others can manage their mentors and members
    - project: project that supervisor is assigned to
    - supervisor: the supervisor we select
    - priority: an integer describes the priority of the supervisor.
    - tasks: assigned task for each supervisor
    - is_email_sent: determines whether a superior has sent email after adding the supervisor to project or not
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    supervisor = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    state = models.CharField(choices=collaborator_states, max_length=200, default="Pending", null=True)
    tasks = models.TextField(null=True, blank=True)
    priority = models.IntegerField(null=False, default=0)
    is_email_sent = models.BooleanField(default=False)
    accept_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.project.title} - {self.supervisor.first_name} {self.supervisor.last_name}"

    class Meta:
        ordering = ['priority']


class ProjectProposal(models.Model):
    project_supervisor = models.ForeignKey(ProjectSupervisor, on_delete=models.CASCADE, null=True, blank=False,
                                           unique=True)
    proposal_file = models.FileField(help_text='It should be in PDF format', upload_to='contracts/',
                                     default="Contract.pdf")
    is_spam = models.BooleanField(default=False)
    project_class = models.CharField(choices=project_classes, max_length=6, default='Normal')

    def __str__(self):
        return f"{self.project_supervisor}"


class ProjectMentor(models.Model):
    """
        Mentors can manage their members
        - project: project that mentor is assigned to
        - supervisor: the supervisor we select
        - priority: an integer describes the priority of the mentors.
        - tasks: assigned task for each mentor
        - is_email_sent: determines whether a superior has sent email after adding the mentor to project or not
    """
    project_supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name="project_mentor_supervisor")
    mentor = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="project_mentor_mentor")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    state = models.CharField(choices=collaborator_states, max_length=200, default="Pending", null=True)
    priority = models.IntegerField(null=False, default=0)
    tasks = models.TextField(null=True, blank=True)
    is_email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.project.title} - {self.mentor.first_name} {self.mentor.last_name}"

    class Meta:
        ordering = ['priority']


class ProjectMember(models.Model):
    """
    Project Member: Since relation between member and project is Many To Many
    - member: member assigned to project
    - project_mentor: mentor of this member, could be a mentor or supervisor
    - priority: an integer describes the priority of the members.
    - tasks: assigned task for each member
    - is_email_sent: determines whether a superior has sent email after adding the member to project or not
    """
    member = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="project_member_member")
    project_mentor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name="project_member_mentor")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    state = models.CharField(choices=collaborator_states, max_length=200, default="Pending", null=True)
    priority = models.IntegerField(null=False, default=0)
    tasks = models.TextField(null=True, blank=True)
    is_email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.member.first_name} {self.member.last_name} - {self.project.title}'

    class Meta:
        ordering = ['priority']


class ProjectLearner(models.Model):
    """
    Project Leaner: Since relation between leaner and project is Many To Many
    - learner: learner assigned to project
    - project_mentor: mentor of this learner, could be a mentor or supervisor
    - priority = models.IntegerField(null=False, default=0)
    - tasks: assigned task for each member
    - is_email_sent: determines whether a superior has sent email after adding the member to project or not
    """
    learner = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="project_learner_learner")
    project_mentor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name="project_learner_mentor")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    state = models.CharField(choices=collaborator_states, max_length=200, default="Pending", null=True)
    priority = models.IntegerField(null=False, default=0)
    tasks = models.TextField(null=True, blank=True)
    is_email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.learner.first_name} {self.learner.last_name} - {self.project.title}'

    class Meta:
        ordering = ['priority']


class ProjectNotification(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    collaborator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    notification = models.CharField(max_length=200, null=False, blank=False)
    notification_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-notification_date']

    def __str__(self):
        return f"{self.project.title} - {self.collaborator}: {self.notification}"


class Visitor(models.Model):
    ip = models.CharField(max_length=50)
    visit_date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"{self.ip} - {self.visit_date}"

class CategoryManager(models.Manager):
    def active(self):
        return self.filter(status=True)

class VideoCategory(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    objects = CategoryManager()

class VideoManager(models.Manager):
    def published(self):
        return self.filter(status='p')


class Video(models.Model):
    STATUS_CHOICE = (
        ('d', 'Draft'),
        ('p', 'Publish'),
        ('i', 'Investigation'),
        ('b', 'Back'),
    )
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=100)
    category = models.ManyToManyField(VideoCategory, related_name="video")
    description = models.TextField()
    link = models.CharField(max_length=500, blank=False, null=False)
    image = models.ImageField(upload_to='archive/video_images/', default='course_default.jpg')
    created = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICE, null=True)
    is_top = models.BooleanField(default=False)
    seen = models.IntegerField(default=0)

    def __str__(self):
        return self.title + " by " + str(self.user.get_full_name())
    
    def category_to_str(self):
        return ", ".join([category.title for category in self.category.active()])

    objects = VideoManager()

class Document(models.Model):
    """
    Document schema: Model to describe each archive document

    -image: thumbnail of the Document we show on archive card
    -title: title of the document (300 letters max)
    -description: a description about the document
    -document_file: uploaded file
    """
    image = models.ImageField(upload_to='archive/document_images/', default='course_default.jpg')
    title = models.CharField(max_length=100)
    description = models.TextField()
    document_file = models.FileField(upload_to="archive/documents/", null=False, blank=False)

    def __str__(self):
        return self.title

class NewsManager(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    is_super_author = models.BooleanField(default=False, verbose_name="Top News Manager")

    def __str__(self):
        return self.manager.first_name + " " + self.manager.last_name

class CategoryManager(models.Manager):
    def active(self):
        return self.filter(status=True)

class NewsCategory(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    objects = CategoryManager()


class ManagerForNews(models.Manager):
    def published(self):
        return self.filter(status='p')

class News(models.Model):
    NEWS_STATUS = (
        ('d', 'Draft'),
        ('p', 'Publish'),
        ('i', 'Investigation'),
        ('b', 'Back'),
    )
    author = models.ForeignKey(NewsManager, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200, null=False, blank=False)
    category = models.ManyToManyField(NewsCategory, related_name="news")
    #description = RichTextField(null=True, blank=False)
    description = models.TextField(null=True, blank=False)
    thumbnail = models.ImageField(upload_to="news_images", verbose_name="Image", null=True)
    date = models.DateField(default=timezone.now, null=True)
    status = models.CharField(max_length=1, choices=NEWS_STATUS, null=True)
    home = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def category_to_str(self):
        return ", ".join([category.title for category in self.category.active()])
    
    def category_list(self):
        return [category.title for category in self.category.active()]

    category_to_str.short_description = "Category"

    class Meta:
        ordering = ['-date']
    
    objects = ManagerForNews()
    
class Event(models.Model):
    EVENT_STATUS = (
        ('d', 'Draft'),
        ('p', 'Publish'),
        ('i', 'Investigation'),
        ('b', 'Back'),
    )
    author = models.ForeignKey(NewsManager, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200, null=False, blank=False)
    description = RichTextField(null=True, blank=False)
    thumbnail = models.ImageField(upload_to="event_images", verbose_name="Image", null=True)
    date = models.DateField(default=timezone.now, null=True)
    status = models.CharField(max_length=1, choices=EVENT_STATUS, null=True)
    home = models.BooleanField(default=False)

    def __str__(self):
        return self.title





def delete_agent(sender, **kwargs):
    """
    Trigger to delete agents after delete a collaborator
    """
    given_collaborator = None
    if type(kwargs['instance']) == ProjectSupervisor:
        given_collaborator = kwargs['instance'].supervisor
    if type(kwargs['instance']) == ProjectMentor:
        given_collaborator = kwargs['instance'].mentor
        if type(kwargs['instance']) == ProjectMember:
            given_collaborator = kwargs['instance'].member

    given_project = kwargs['instance'].project
    if given_project.agent == given_collaborator:
        given_project.agent = None
        given_project.agent_permission = False
        given_project.save()


pre_delete.connect(delete_agent, sender=ProjectSupervisor)
pre_delete.connect(delete_agent, sender=ProjectMentor)
pre_delete.connect(delete_agent, sender=ProjectMember)

class SuggestionBox(models.Model):
    Departments=(
    ('Site','Site section'),
    ('Project','Project section'),
    ('Advertisement','Advertisement section'),
    ('Administrative ','Administrative section'),
    ('Workshop','Workshop section'),
    ('Administratorship','Administratorship'),
    )
    email = models.EmailField()
    department=models.CharField(max_length=300,choices=Departments,null=True)
    title = models.CharField(max_length=150)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    is_read=models.BooleanField(default=0)
    is_reply=models.BooleanField(default=0)
    reply_date=models.DateTimeField(null=True)
    reply_message=models.TextField(max_length=5000,null=True)

    def __str__(self):
        return self.title



