from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
from PIL import Image
from django.utils.translation import gettext_lazy as _

from ivc_website.models import IndustrialArea

refer_choices = (
    ('Friends', 'Friends'),
    ('Instagram', 'Instagram'),
    ('Twitter', 'Twitter'),
    ('Telegram', 'Telegram'),
    ('Linkedin', 'Linkedin'),
    ('Search Engine', 'Search Engine'),
)
position_choices = (
    (_("Learner"), _("Learner")),
    (_("Member"), _("Member")),
    (_("Mentor"), _("Mentor")),
    (_("Supervisor"), _("Supervisor")),
)
degree_choices = (
    ("Diploma", "Diploma"),
    ("Bachelor's degree", "Bachelor's degree"),
    ("Master's degree", "Master's degree"),
    ("Doctoral degree", "Doctoral degree"),
)
interest_choices = (
    ("Machine Learning", "Machine Learning"),
    ("Programming", "Programming"),
    ("Physical Sciences", "Physical Sciences"),
    ("Maths & Computing ", "Maths & Computing "),
    ("Law", "Law"),
    ("Humanities & Art", "Humanities & Art"),
    ("Engineering", "Engineering"),
    ("Earth Sciences", "Earth Sciences"),
    ("Chemical Sciences", "Chemical Sciences"),
    ("Business & Finance", "Business & Finance"),
    ("	Biological & Medical Sciences", "	Biological & Medical Sciences"),
)

area_choices = {
    ("Machine Learning", "Machine Learning"),
    ("Deep Learning", "Deep Learning"),
    ("Statistics", "Statistics"),
    ("Medical Physics", "Medical Physics"),
}

status_choices = [
    ('Student', 'Student'),
    ('Assistant-professor', 'Assistant professor'),
    ('Associate-professor', 'Associate professor'),
    ('Professor', 'Professor'),
    ('Employee', 'Employee'),
    ('Company Manager', 'Company Manager'),
    ("Post-Doctoral", "Post-Doctoral"),
    ("Other", "Other"),
]
sex_choices = {
    ('Male', 'Male'),
    ('Female', 'Female'),
}

field_of_study_choices = [
    ('Accounting and Financial Management', 'Accounting and Financial Management'),
    ('Aerospace Engineering', 'Aerospace Engineering'),
    ('Archaeology', 'Archaeology'),
    ('Architecture', 'Architecture'),
    ('Arts and Humanities', 'Arts and Humanities'),
    ('Artificial Intelligence', 'Artificial Intelligence'),
    ('Biochemistry', 'Biochemistry'),
    ('Bioengineering', 'Bioengineering'),
    ('Bioinformatics ', 'Bioinformatics '),
    ('Biology ', 'Biology '),
    ('Biomedical Engineering', 'Biomedical Engineering'),
    ('Biotechnology', 'Biotechnology'),
    ('Business', 'Business'),
    ('Cardiovascular Science', 'Cardiovascular Science'),
    ('Cell Biology', 'Cell Biology'),
    ('Chemical and Biological Engineering (CBE)', 'Chemical and Biological Engineering (CBE)'),
    ('Chemistry ', 'Chemistry '),
    ('Civil and Structural Engineering', 'Civil and Structural Engineering'),
    ('Clinical Psychiatry', 'Clinical Psychiatry'),
    ('Computer Engineering', 'Computer Engineering'),
    ('Computer Science', 'Computer Science'),
    ('Criminology', 'Criminology'),
    ('Dentistry', 'Dentistry'),
    ('Data Science', 'Data Science'),
    ('Ecology', 'Ecology'),
    ('Electronic and Electrical Engineering', 'Electronic and Electrical Engineering'),
    ('Electronic Control and Systems Engineering', 'Electronic Control and Systems Engineering'),
    ('Economics', 'Economics'),
    ('Electrical Engineering', 'Electrical Engineering'),
    ('Environmental Engineering', 'Environmental Engineering'),
    ('Genetics', 'Genetics'),
    ('Genomics', 'Genomics'),
    ('Geography', 'Geography'),
    ('Health Sciences', 'Health Sciences'),
    ('Hispanic', 'Hispanic'),
    ('History', 'History'),
    ('Human Communication Sciences', 'Human Communication Sciences'),
    ('Human Metabolism', 'Human Metabolism'),
    ('Human Nutrition', 'Human Nutrition'),
    ('Information', 'Information'),
    ('International Relations', 'International Relations'),
    ('Industrial Engineering', 'Industrial Engineering'),
    ('Immunity and Cardiovascular Disease', 'Immunity and Cardiovascular Disease'),
    ('Journalism ', 'Journalism '),
    ('Landscape Architecture ', 'Landscape Architecture '),
    ('Languages and Cultures ', 'Languages and Cultures '),
    ('Law ', 'Law '),
    ('Linguistics ', 'Linguistics '),
    ('Management  ', 'Management  '),
    ('Mechatronics ', 'Mechatronics '),
    ('Material Science', 'Material Science'),
    ('Mathematics', 'Mathematics'),
    ('Metabolism ', 'Metabolism '),
    ('Mechanical Engineering', 'Mechanical Engineering'),
    ('Medical Informatics', 'Medical Informatics'),
    ('Medical Physics', 'Medical Physics'),
    ('Medicine', 'Medicine'),
    ('Medical Engineering', 'Medical Engineering'),
    ('Medical Imaging', 'Medical Imaging'),
    ('Microbiology ', 'Microbiology '),
    ('Microelectronics ', 'Microelectronics '),
    ('Modern Languages and Linguistics', 'Modern Languages and Linguistics'),
    ('Molecular Biology and Biotechnology ', 'Molecular Biology and Biotechnology '),
    ('Music', 'Music'),
    ('Neuroscience', 'Neuroscience'),
    ('Nursing and Midwifery', 'Nursing and Midwifery'),
    ('Nuclear Engineering', 'Nuclear Engineering'),
    ('Nuclear Medicine Physician', 'Nuclear Medicine Physician'),
    ('Nuclear physics', 'Nuclear physics'),
    ('Ophthalmology and Orthoptics', 'Ophthalmology and Orthoptics'),
    ('Pharmacology', 'Pharmacology'),
    ('Philosophy', 'Philosophy'),
    ('Physics', 'Physics'),
    ('Physics and Astronomy', 'Physics and Astronomy'),
    ('Physiology', 'Physiology'),
    ('Plant Sciences', 'Plant Sciences'),
    ('Politics and International Relations', 'Politics and International Relations'),
    ('Psychology', 'Psychology'),
    ('Robotics', 'Robotics'),
    ('Social Sciences', 'Social Sciences'),
    ('Sociological Studies', 'Sociological Studies'),
    ('Software Engineering', 'Software Engineering'),
    ('Speech Science ', 'Speech Science '),
    ('Statistics', 'Statistics'),
    ('Speech Science ', 'Speech Science '),
    ('Systems Engineering', 'Systems Engineering'),
    ('Town and Regional Planning', 'Town and Regional Planning'),
    ('Urban Studies and Planning', 'Urban Studies and Planning'),
    ('Work Psychology', 'Work Psychology'),
    ('Zoology', 'Zoology'),
    ('Other', 'Other')
]

contact_preference_choices = [
    ('Email Address', 'Email Address'),
    ("Phone Number", "Phone Number"),
    ("Skype", "Skype")
] 

class MemberProfile(models.Model):
    """
    Profile for users
    - user: user that we're gonna build profile for him
    - image: Profile Image
    - position: Member, Mentor or Supervisor, by default it's Member
    - is_guest: by default every user is a guest user
    - field of study
    - status: user has to choose based on status_choices
    - degree: user has to choose between degree_choices
    - interest: user has to choose between interest_choices
    - description: a short description of that user
    - cv_file: pdf file that user uploaded when joined to tecvico. it has to be in pdf format (mandatory)
    - skype: skype ID
    - priority: user priority to be seen on members list. less number means higher priority
    """
    check_all = models.BooleanField(default=False, null=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default_profile.jpg', upload_to='members/images', verbose_name=_('Image'), null= True)
    position = models.CharField(max_length=30, choices=position_choices, default='Member',
                                verbose_name=_('Position'))
    is_guest = models.BooleanField(default=True)
    is_technical_manager = models.BooleanField(default=False)
    is_research_director = models.BooleanField(default=False)
    field_of_study = models.CharField(max_length=150, choices=field_of_study_choices, verbose_name=_('Field Of Study'))
    status = models.CharField(max_length=50, choices=status_choices, verbose_name=_('Status'), null=True, blank=False)
    degree = models.CharField(max_length=50, choices=degree_choices, default=_("Bachelor's degree"),
                              verbose_name=_('Degree'))
    interest = MultiSelectField(choices=interest_choices, null=True, verbose_name=_('Interest'), blank=False)
    about_me = models.TextField(null=True, verbose_name=_('About Me'))
    birthday = models.DateField(null=True, verbose_name=_('Birthday'))
    gender = models.CharField(max_length=6, choices=sex_choices, null=True, verbose_name=_('Gender'))
    time_can_spend_per_day = models.PositiveIntegerField(null=True, help_text=_("Unit is hour"),
                                                         verbose_name=_('Time Can Spend Per Day'))

    phone = models.CharField(max_length=17, null=True, verbose_name=_('Phone'))
    phone_region = models.CharField(max_length=5, default='IR')

    university = models.CharField(max_length=100, null=True, help_text=_("This is the university you graduated or "
                                                                         "you're studying now"),
                                  verbose_name=_('University'))
    city = models.CharField(max_length=100, null=True, verbose_name=_('City'))
    country = models.CharField(max_length=100, null=True, verbose_name=_('Country'))
    cv_file = models.FileField(upload_to='applicants/pdf', null=False, blank=False, default='default.pdf',
                               verbose_name=_('CV file'))
    skype = models.CharField(max_length=200, null=True, blank=True, help_text="Your skype ID")
    priority = models.IntegerField(default=0, verbose_name=_('Priority'))
    special_member_access = models.BooleanField(default=False)
    referred_by = models.CharField(max_length=200, null=True, blank=True, verbose_name=_("Referred by"),
                                   choices=refer_choices)

    # score
    balance = models.IntegerField(default=0)

    is_internship = models.BooleanField(default=False, verbose_name=_("Internship"))
    
    topic_count_warning = models.IntegerField(null=True, default=0, editable=False)
    forum_block_topic = models.BooleanField(default=False, null=True, editable=False)
    forum_date_block_topic = models.DateTimeField(default=None, null=True, editable=False)
    
    
    comment_count_warning = models.IntegerField(null=True, default=0, editable=False)
    forum_date_block_comment = models.DateTimeField(default=None, null=True, editable=False)
    forum_block_comment = models.BooleanField(default=False, null=True, editable=False)

    count_expert_change_request = models.IntegerField(null=True, default=0, blank=True, editable=False)
    expert_change_request = models.TextField(null=True, blank=True, editable=False)
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)

        output_size = (400, 400)
        img.thumbnail(output_size)
        img.save(self.image.path)


class LegalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    company_name = models.CharField(max_length=100, verbose_name=_('Company Name'))
    work_area = models.CharField(max_length=200, verbose_name=_('Work Area'), null=True, blank=False)
    about_company = models.TextField(null=True, verbose_name=_('About Company'))

    phone = models.CharField(max_length=17, null=True, verbose_name=_('Phone'))
    phone_region = models.CharField(max_length=5, default='IR')
    fax = models.CharField(max_length=30, null=True, blank=True, verbose_name=_('Fax'))

    city = models.CharField(max_length=100, null=True, blank=False, verbose_name=_('City'))
    country = models.CharField(max_length=100, null=True, blank=False, verbose_name=_('Country'))
    street = models.CharField(max_length=100, null=True, blank=False, verbose_name=_('Street'))
    zip_code = models.CharField(max_length=50, null=True, blank=False, verbose_name=_('Zip Code'))

    registration_number = models.CharField(max_length=50, null=True, blank=False, verbose_name=_('Registration Number'))

    image = models.ImageField(default='default_legal.png', upload_to='members/images', verbose_name=_('Image'),
                              null=True, blank=True)

    skype = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Skype'))
    instagram = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Instagram'))
    linkedin = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Linkedin'))
    telegram = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Telegram'))

    contact_preference = models.CharField(max_length=100, null=True, blank=True, choices=contact_preference_choices)

    def __str__(self):
        return f"{self.user} - {self.company_name}"


class Interviewer(models.Model):
    """
    The staff that are responsible to interview recently added members and give experience badges to them
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Expert(models.Model):
    """
    Users that are eligible to be an expert for a particular INDUSTRIAL project
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class ResearchExpert(models.Model):
    """
    Users that are eligible to be a research expert for a particular RESEARCH project
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class ExpertArea(models.Model):
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE, null=True, blank=True)
    area = models.ForeignKey(IndustrialArea, on_delete=models.CASCADE)
    agree = models.BooleanField(null=True)
    disagree = models.BooleanField(null=True)

    def __str__(self):
        return f"{self.expert.user} - {self.area} | Agree: {self.agree}"


class TopSupervisor(models.Model):
    profile = models.ForeignKey(MemberProfile, on_delete=models.CASCADE)
    company_position = models.CharField(max_length=70, null=False, blank=False, default="Not Determined")
    email = models.EmailField(null=True)
    linkedin_url = models.URLField(null=True, blank=True)
    twitter_url = models.URLField(null=True, blank=True)
    facebook_url = models.URLField(null=True, blank=True)
    instagram_url = models.URLField(null=True, blank=True)
    homepage_url = models.URLField(null=True, blank=True)
    priority = models.IntegerField(default=0)

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return f"{self.profile.user.first_name} {self.profile.user.last_name} - Priority: {self.priority}"


class CompanyMail(models.Model):
    """
    For each member, we create an email and use this table just to make sure they have seen that
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    initial_password = models.CharField(max_length=10)
    has_seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}"


class Role(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "role")
    position = models.CharField(max_length=50, default="")
    email = models.EmailField(null=True, max_length=256,blank=True,unique=True)
    def __str__(self):
        return f"id={self.user.id} - {self.user.first_name} {self.user.last_name} - position={self.position}"