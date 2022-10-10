from distutils.command.upload import upload
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Guarante(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.user.username


class MainField(models.Model):
    title = models.CharField(max_length=100, default=None)
    slug = models.SlugField(max_length=100, unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class SubField(models.Model):
    parent = models.ForeignKey(MainField, null=True ,related_name='mainfield', on_delete=models.SET_NULL)
    title = models.CharField(max_length=100, default=None)
    slug = models.SlugField(max_length=100, unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.title  
        
class Workshop(models.Model):
    unique_id = models.CharField(max_length=30)
    capacity = models.IntegerField(default=0, null=True)
    is_online = models.BooleanField(default=False)
    top_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'dawdn')
    guaranteed = models.ForeignKey(Guarante, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=1000)
    time_to_start = models.TimeField(default=timezone.now())
    date = models.DateField(default=timezone.now())
    price = models.IntegerField(null=True)
    duration = models.CharField(max_length=50, default=0)
    main_field = models.ForeignKey(MainField, null=True, on_delete=models.SET_NULL, related_name="workshop")
    sub_field = models.ForeignKey(SubField, null=True, on_delete=models.SET_NULL, related_name="workshop")
    image = models.ImageField(upload_to="workshop/")
    load_pdf = models.FileField(default="", upload_to="workshop/", max_length=500)  # pdf & powerpoint
    description = models.TextField(max_length=5000)
    address = models.TextField(max_length=1000)
    prev_experience = models.TextField(max_length=2500)
    work_with_us = models.IntegerField(null=True, default=0)
    work_with_others = models.IntegerField(null=True, default=0)
    proof_file = models.FileField(default="", upload_to="workshop/", null=True)
    language = models.CharField(max_length=1000, null=True)
    speaker = models.CharField(max_length=1000, null=True)
    suggest_country = models.CharField(max_length=1000, null=True)
    keyword = models.CharField(max_length=1000, null=True)
    skills = models.CharField(max_length=1000, null=True)
    video = models.CharField(max_length=200, null=True, default="")
    status = models.CharField(max_length=30, default="Set_time_table")
    created = models.DateTimeField(auto_now_add=True)
    time_zone = models.CharField(max_length=1000, default="", null=True)
    add_field = models.CharField(max_length=1000, default="", null=True)

    def __str__(self):
        return f"workshop_id={self.id} - {self.title} - {self.date} - {self.price}"

    def create_date(self):
        return self.created.date()


class Comment(models.Model):
    STATUS_CHIOCE = (
        ('New', 'New'),
        ('Approve', 'Approve'),
        ('Decline', 'Decline'),
    )
    expert = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'dawdnad')
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name = 'expert_comment')
    comment = models.TextField(max_length=200)
    is_checked = models.BooleanField(default=False,null=True)
    expert_price = models.IntegerField(default=0,null=True)
    access = models.BooleanField(default=False,null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHIOCE, default="New")
    
    def __str__(self):
        return f"{self.workshop.title} - {self.expert.first_name}"

class Users_Workshops(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #user_id = models.IntegerField(null=True, default=0)
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    section=models.CharField(max_length=50,default='All',blank=True)
    certificate=models.FileField(upload_to="workshop/certificates/",null=True,default=None)

    def __str__(self):
        return str(self.user.get_full_name()) + " " + self.workshop.title

class AcceptReject(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    workshop = models.OneToOneField(Workshop, on_delete=models.CASCADE, related_name = 'accept_reject')
    is_accept = models.BooleanField(default=False)
    comment = models.TextField(max_length=200, null=True)
    is_edited = models.BooleanField(default=False)
    approve_contract=models.BooleanField(default=False,null=True)
    contract=models.FileField(upload_to="workshop/contracts/",null=True,default=None)
    
    def __str__(self):
        return str(self.workshop)


class Role(models.Model):
    pos = models.TextField(max_length=50, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'dawdnbge')
    def __str__(self):
        return f"{self.pos}"
        

class TimeTable(models.Model):
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE)
    title=models.CharField(max_length=50,null=True)
    start_date=models.DateField(null=True)
    start_time=models.CharField(max_length=50,null=True)
    end_time=models.CharField(max_length=50,null=True)
    duration=models.CharField(max_length=50,null=True)
    price=models.IntegerField(null=True)
    expert_price=models.IntegerField(null=True)
    video_link=models.CharField(max_length=200,null=True)
    information = models.FileField(null=True,upload_to='workshop/time_table/')

    def __str__(self):
        return self.workshop.title




#Lotfi-.-.-.-.-.-.-.-.--.-.-.-.-.-.-.
class Adverstiment(models.Model):
    title=models.TextField(max_length=5000)
    coursetitles=models.TextField(max_length=5000)
    courseclients=models.TextField(max_length=5000)
    certificatedesc=models.TextField(max_length=5000)
    content=models.TextField(max_length=5000)
    coursespeakers=models.TextField(max_length=5000)
    logo_image=models.ImageField(upload_to='workshop/')
    contracts=models.FileField(upload_to='workshop/contracts/')
    workshop=models.ForeignKey(Workshop,on_delete=models.CASCADE,null=True)


class LandingPage(models.Model):
    direction=models.CharField(max_length=30,default='ltr')
    title=models.CharField(max_length=100)
    coursetitles_title=models.CharField(max_length=50)
    coursetitles=models.TextField(max_length=5000)
    courseclients_title=models.CharField(max_length=50)
    courseclients=models.TextField(max_length=5000)
    certificate_title=models.CharField(max_length=50)
    certificatedesc=models.TextField(max_length=5000)
    content=models.TextField(max_length=20000)
    coursespeakers_title=models.CharField(max_length=50)
    coursespeakers=models.TextField(max_length=10000)
    registeration_title=models.CharField(max_length=50)
    registeration_content=models.TextField(max_length=20000)
    logo_image=models.ImageField(blank=True,upload_to="workshop/")
    banner_image=models.ImageField(upload_to="workshop/")
    workshop=models.ForeignKey(Workshop,on_delete=models.CASCADE)



class Workshop_log(models.Model):
    position_value=(
            ('expert','expert'),
            ('director','director'),
            ('supervisor','supervisor'),
        )
    desc=(
        ('pay_guarante','workshop created by supervisor and pending for pay guarante'),
        ('Notpay','Create invoice by supervisor but not paid yet'),
        ('Guarante_accept','supervisor pay invoice and workshop send to director for select expert'),
        ('Expert_decide','workshop send to expert by director'),
        ('reject_expert','workshop decline by expert'),
    )
    class description(models.TextChoices):
        pay_guarante =_('workshop created by supervisor and pending for pay guarante')
        Notpay =_('Create invoice by supervisor but not paid yet')
        Guarante_accept =_('supervisor pay invoice and workshop send to director for select expert')
        Expert_decide =_('workshop send to expert by director')
        reject_expert = _('workshop decline by expert')
        Expert_comment=_('Expert accept evaluate workshop')
        Manager_check=_('Expert evaluated workshop')
        Manager_check_from_supervisor=_('supervisor edit workshop')
        Accept=_('Workshop accepted by director')
        Revise_to_expert=_('Workshop revise by director')
        Reject=_('Workshop reject by director')
        Approve_contract=_('Director approved the workshop and now expert has to sending the contract for supervisor')
        Upload_contract=_('Expert upload contract and send to supervisor for assign')
        Send_contract_by_supervisor=_('Supervisor send contract to expert')
        Revise_contract_to_supervisor=_('Expert wants the revising the contract and to send contract to supervisor')
        Send_contract_to_director=_('Expert sent contract to director')
        REVISE_CONTRACT_TO_EXPERT=_('Contract revise by director and send to expert')
        Reject_contract_to_supervisor=_("Director rejected contract")

        SEND_CONTRACT_TO_SUPERVISOR=_('Contract send to supervisor')

    position=models.CharField(max_length=50,choices=position_value,default='supervisor')
    status=models.CharField(max_length=100,null=True,default='create_workshop')
    desc=models.TextField(max_length=1000,choices=description.choices,default=description.pay_guarante)
    created=models.DateTimeField(auto_now_add=True)
    workshop=models.ForeignKey(Workshop,on_delete=models.CASCADE)
    to_do=models.BooleanField(default=True)
    is_done=models.BooleanField(default=False)
    step=models.IntegerField(default=1)


DIRECTOR_STATUS=[
    {'status':'New','msg':_("Pending for guarantor's response")},
    {'status':'pay_guarante','msg':_('Pending for paying responsibility fee')},
    {'status':'Set_time_table','msg':_('Pending for setting timetable')},
    {'status':'Notpay','msg':_('Notpay')},
    {'status':'Guarante_accept','msg':_('You should select an expert')},
    {'status':'Expert_decide','msg':_("Pending for expert's approval")},
    {'status':'reject_expert','msg':_('Has been rejected by you')},
    {'status':'Expert_comment','msg':_("Pending for expert's decision")},
    {'status':'Manager_check','msg':_("Pending for  director's decision")},
    {'status':'Manager_check_from_supervisor','msg':_('Manager_check_from_supervisor')},
    {'status':'Revise_to_expert','msg':_('Revising to expert by you')},
    {'status':'Reject','msg':_('Rejected to supervisor')},
    {'status':'Accept','msg':_('Accepted')},
    {'status':'Delete','msg':_('Deleted')},
    {'status':'Approve_contract','msg':_("Pending for expert's action to sending contract")},
    {'status':'Upload_contract','msg':_("Pending for supervisor decision")},
    {'status':'Send_contract_by_supervisor','msg':_("Supervisor send contract to expert")},
    {'status':'Revise_contract_to_supervisor','msg':_("Expert wants the revising the contract ")},
    {'status':'Send_contract_to_director','msg':_("Pending for  director's decision ")},
    {'status':'Revise_contract_to_expert','msg':_("Contract for revise to  expert sent")},
    {'status':'Reject_contract_to_supervisor','msg':_("Director rejected contract to supervisor")},

    {'status':'send_contract_to_supervisor','msg':_("Pending for to send contract by supervisor")},

]


EXPERT_STATUS=[
    {'status':'pay_guarante','msg':_('')},
    {'status':'Notpay','msg':_('')},
    {'status':'Guarante_accept','msg':_('')},
    {'status':'Expert_decide','msg':_('Pending for your decision')},
    {'status':'reject_expert','msg':_('Has been rejected by you')},
    {'status':'Expert_comment','msg':_('Pending for your evaluation')},
    {'status':'Manager_check','msg':_("Pending for director's decission")},
    {'status':'Manager_check_from_supervisor','msg':_("Pending for director's decission")},
    {'status':'Revise_to_expert','msg':_('Director wants you revising')},
    {'status':'Reject','msg':_('Rejected to supervisor')},
    {'status':'Accept','msg':_('Accepted')},
    {'status':'Delete','msg':_('Deleted')},
    {'status':'Approve_contract','msg':_("Pending for to sending contract to supervisor")},
    {'status':'Upload_contract','msg':_("Pending for supervisor's decision")},
    {'status':'Send_contract_by_supervisor','msg':_("Pending your decision")},
    {'status':'Revise_contract_to_supervisor','msg':_("You  wants the revising the contract ")},
    {'status':'Send_contract_to_director','msg':_("Pending for  director's decision ")},
    {'status':'Revise_contract_to_expert','msg':_("pending for your revise")},
    {'status':'Reject_contract_to_supervisor','msg':_("Director rejected contract to supervisor")},

    {'status':'send_contract_to_supervisor','msg':_("Pending for to send contract by supervisor")},

]

SUPERVISOR_STATUS=[
    {'status':'pay_guarante','msg':_('Pending for paying responsibility fee')},
    {'status':'New','msg':_("Pending for the guarantor's response")},
    {'status':'Set_time_table','msg':_("To finialize the submission you must set the timetable")},
    {'status':'Notpay','msg':_('Notpay')},
    {'status':'Guarante_accept','msg':_('Under process')},
    {'status':'Expert_decide','msg':_('Under process')},
    {'status':'reject_expert','msg':_('Under process')},
    {'status':'Expert_comment','msg':_('Under process')},
    {'status':'Manager_check','msg':_('Under process')},
    {'status':'Manager_check_from_supervisor','msg':_('Under process')},
    {'status':'Revise_to_expert','msg':_('Under process')},
    {'status':'Reject','msg':_('Rejected by director')},
    {'status':'Accept','msg':_('Accepted')},
    {'status':'Delete','msg':_('Deleted')},
    {'status':'Approve_contract','msg':_("Under process")},
    {'status':'Upload_contract','msg':_("Waiting for your confirmation and signature of the contract")},
    {'status':'Send_contract_by_supervisor','msg':_("Under process")},
    {'status':'Revise_contract_to_supervisor','msg':_("Pending for your decision ")},
    {'status':'Send_contract_to_director','msg':_("Under process")},
    {'status':'Revise_contract_to_expert','msg':_("Under process")},
    {'status':'Reject_contract_to_supervisor','msg':_("Director rejected contract to you pending for your decision")},
    
    {'status':'send_contract_to_supervisor','msg':_("Pending for your decision")},

]
