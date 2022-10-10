from calendar import c
from datetime import date
from heapq import merge
import json
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from django.urls import reverse_lazy
from users.models import MemberProfile
from django.http import Http404, JsonResponse, request
from research.models import ResearchProject
from django.template.loader import get_template
from ivc_project.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string
from ivc_project.settings import DEFAULTE_HOST_USER
from workshop.models import Workshop, Users_Workshops, TimeTable
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.core.mail import send_mail, EmailMultiAlternatives, get_connection, EmailMessage
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from .mixins import *
from .models import *
from .forms import *
from ivc_project.settings import EMAIL_HOST_USER
from django.core import serializers
from django.urls import reverse
from django.contrib import messages
from django.utils.html import strip_tags
# Create your views here.

class Home(ListView):
    queryset = Company.objects.Active()
    template_name = 'emails/home.html'
    def get_queryset(self):
        companies=Company.objects.Active().order_by("-created")
        for company in companies:
            company.emails_count=Emails.objects.filter(company=company).count()
        return companies
    def get_context_data(self, **kwargs):
        institutes=Institute.objects.filter(status="visible").order_by("-created")
        for institute in institutes:
            institute.emails_count=EmailsInstitute.objects.filter(institute=institute).count()
        
        context = super().get_context_data(**kwargs)
        context['category_temp'] = CategoryTemplate.objects.filter(status="visible").order_by("-created")
        context['institutes'] =institutes 
        context['workshops'] = Workshop.objects.filter(status="Accept")
        context['company_count'] = CategoryTemplate.objects.filter(status="visible").count()
        context['category_temp_count'] = CategoryTemplate.objects.filter(status="visible").count()
        context['institutes_count'] = Institute.objects.filter(status="visible").count()
        context['tags'] = Tag.objects.all()
        return context

def detail_workshop(request, pk):
    template_name = 'emails/detail-workshop.html'
    obj_workshop = get_object_or_404(Workshop, status='Accept', pk=pk)
    
    workshop_speaker = obj_workshop.speaker
    speakers = workshop_speaker.split(',')
    context = {
        'object': obj_workshop,
        'speakers':speakers,
        'Users_Workshops': Users_Workshops.objects.filter(workshop=obj_workshop)
    }
    return render(request, template_name, context)


def detail_institute(request, pk):
    template_name = 'emails/detail-institute.html'
    obj_institute = get_object_or_404(Institute, status='visible', pk=pk)
    
    emails=EmailsInstitute.objects.filter(institute=obj_institute).all()
    for email in emails:
        if SendEmail.objects.filter(email=email).exists():
            email.send=SendEmail.objects.filter(email=email).all()

    obj_institute_country=Country.objects.filter(title=obj_institute.country).first()
 
    departments_path = os.path.join(os.path.dirname(__file__), 'departments.txt')
    readdepartments = open(departments_path , 'r')
    readdepartments.seek(0)
    readdepartments=readdepartments.readlines()
    departments=[]
    for i in readdepartments:
        if not i.strip():
           continue
        if i:
           department_exist=DepartmentInstitu.objects.filter(name=i).first()
           if department_exist is None:
               new_department=DepartmentInstitu.objects.create(user=request.user,name=i,approove=False)
           departments.append(i)
    approve_departments=DepartmentInstitu.objects.filter(approove=True).all()

    if request.method == "POST":
        form_delete_c = DeleteCompanyForm(request.POST, request.FILES)
        form_delete_e = DeleteEmailForm(request.POST, request.FILES)

        if form_delete_e.is_valid():
            status = form_delete_e.cleaned_data.get("status")
            email_id = form_delete_e.cleaned_data.get("email_id")

            obj_email = EmailsInstitute.objects.get(id=email_id)
            
            obj_email.status = 'deleted'
            obj_email.email_address += ' - deleted'
            obj_email.deleted_user = request.user
            obj_email.save()
            return redirect("email:detail-institute", obj_institute.pk)

        elif form_delete_c.is_valid():
            status = form_delete_c.cleaned_data.get("status")

            obj_institute.status = 'deleted'
            obj_institute.deletor = request.user
            obj_institute.save()
            return redirect("email:home")

    else:
        form_delete_e = DeleteEmailForm
        form_delete_c = DeleteCompanyForm

    linkdin_filter=[]
    all_email=EmailsInstitute.objects.all()
    for email in all_email:
        if email.linkdin == None or email.linkdin == '':
            pass
        else:
            linkdin_filter.append(email)
            
    context = {
    'object': obj_institute,
    'obj_institute_country':obj_institute_country,
    'form_delete_c': form_delete_c,
    'form_delete_e': form_delete_e,
    'country': Country.objects.all(),
    'departments':approve_departments,
    'emails':emails,
    'tags':Tag.objects.all(),
    'linkdins':linkdin_filter
    }
    return render(request, template_name, context)

def create_email_institute(request):
    id_institute =  int(request.POST.get("id_institute"))
    degree =  request.POST.get("degree")
    gender =  request.POST.get("gender")
    position =  request.POST.get("position")
    full_name =  request.POST.get("full_name")
    department =  request.POST.get("department")
    email_address =  request.POST.get("email_address")
    google_scholar =  request.POST.get("google_scholar")
    laboratory_website =  request.POST.get("laboratory_website")
    linkdin =  request.POST.get("linkdin")
    linkdin_nick =  request.POST.get("linkdin_nick")
    tags =  request.POST.get("tags")

    obj_institute = Institute.objects.get(id=id_institute)

    create_email = EmailsInstitute.objects.create(
        degree=degree, gender=gender, position=position, 
        full_name=full_name, department=department, email_address=email_address, 
        google_scholar=google_scholar, laboratory_website=laboratory_website, creator=request.user,
        institute=obj_institute,linkdin=linkdin,linkdin_nick=linkdin_nick,tags=tags)
    messages.success(request, 'Email created successfully.')
    return redirect("email:detail-institute", obj_institute.pk)



def edit_email_institute(request):
    id_email =  int(request.POST.get("id_email"))
    id_institute =  int(request.POST.get("id_institute"))
    degree =  request.POST.get("degree")
    gender =  request.POST.get("gender")
    position =  request.POST.get("position")
    full_name =  request.POST.get("full_name")
    department =  request.POST.get("department")
    email_address =  request.POST.get("email_address")
    google_scholar =  request.POST.get("google_scholar")
    laboratory_website =  request.POST.get("laboratory_website")
    linkdin =  request.POST.get("linkdin")
    linkdin_nick =  request.POST.get("linkdin_nick")
    tags =  request.POST.get("tags")

    request_user = str(request.user)
    obj_institute = Institute.objects.get(id=id_institute)
    email_obj = EmailsInstitute.objects.get(id=id_email)

    email_obj.degree = degree
    email_obj.gender = gender
    email_obj.position = position
    email_obj.full_name = full_name
    email_obj.department = department
    email_obj.email_address = email_address
    email_obj.google_scholar = google_scholar
    email_obj.linkdin = linkdin
    email_obj.linkdin_nick = linkdin_nick
    email_obj.laboratory_website = laboratory_website
    email_obj.tags = tags
    email_obj.last_editor += request_user
    email_obj.last_editor += ', '
    email_obj.save()
    return redirect("email:detail-institute", obj_institute.pk)


def edit_institute(request):
    id_institute =  request.POST.get("id_institute")
    country = request.POST.get('country')
    location = request.POST.get('location')
    web_address = request.POST.get('web_address')
    web_page = request.POST.get('web_page')
    institute_name = request.POST.get('institute_name')

    request_user = str(request.user)

    obj_institute = Institute.objects.get(id=id_institute)

    obj_institute.country_id = country
    obj_institute.location = location
    obj_institute.web_address = web_address
    obj_institute.web_page = web_page
    obj_institute.institute_name = institute_name
    obj_institute.last_editor += request_user
    obj_institute.last_editor += ', '
    obj_institute.save()


    return redirect("email:detail-institute", obj_institute.pk)




def detail_company(request, pk,*args,**kwargs):
    template_name = 'emails/detail-compnay.html'
    obj_company = get_object_or_404(Company, pk=pk)

    emails=Emails.objects.filter(company=obj_company).all()
    for email in emails:
        if SendEmail.objects.filter(email=email).exists():
            email.send=SendEmail.objects.filter(email=email).all()

    if request.method == "POST":
        form_delete_e = DeleteEmailForm(request.POST, request.FILES)
        form_accept = CreateEmailForm(request.POST, request.FILES)
        form_delete_c = DeleteCompanyForm(request.POST, request.FILES)
        form_update_e = UpdateEmailForm(request.POST, request.FILES)
        if form_delete_e.is_valid():
            status = form_delete_e.cleaned_data.get("status")
            email_id = form_delete_e.cleaned_data.get("email_id")
            request_user = request.user
            request_user = str(request_user)

            obj_email = Emails.objects.get(id=email_id)
            
            obj_email.status = 'deleted'
            obj_email.agent_email_address += ' - deleted'
            obj_email.deleted_user = request_user
            obj_email.save()
            return redirect("email:detail-category", obj_company.pk)

        elif form_delete_c.is_valid():
            status = form_delete_c.cleaned_data.get("status")
            request_user = request.user
            request_user = str(request_user)

            obj_company.status = 'deleted'
            obj_company.deleted_user = request_user
            obj_company.save()
            return redirect("email:home")


        elif form_accept.is_valid():
            gender = form_accept.cleaned_data.get("gender")
            agent_position = form_accept.cleaned_data.get("agent_position")
            agent_email_address = form_accept.cleaned_data.get("agent_email_address")
            company_agent_surname = form_accept.cleaned_data.get("company_agent_surname")
            agent_academic_degree = form_accept.cleaned_data.get("agent_academic_degree")
            company_agent_first_name = form_accept.cleaned_data.get("company_agent_first_name")
            tags = request.POST.get("tags")

            create_email = Emails.objects.create(
                gender=gender, agent_position=agent_position, agent_email_address=agent_email_address, 
                company_agent_surname=company_agent_surname, agent_academic_degree=agent_academic_degree, 
                company_agent_first_name=company_agent_first_name, company=obj_company, creator=request.user,tags=tags)
            messages.success(request, 'Email created successfully.')

            return redirect("email:detail-category", obj_company.pk)


        elif form_update_e.is_valid():
            gender = form_update_e.cleaned_data.get("gender")
            email_id = int(form_update_e.cleaned_data.get("email_id"))
            agent_position = form_update_e.cleaned_data.get("agent_position")
            agent_email_address = form_update_e.cleaned_data.get("agent_email_address")
            company_agent_surname = form_update_e.cleaned_data.get("company_agent_surname")
            agent_academic_degree = form_update_e.cleaned_data.get("agent_academic_degree")
            company_first_name = form_update_e.cleaned_data.get("company_first_name")
            tags = request.POST.get("tags")

            email_obj = Emails.objects.get(id=email_id)

            email_obj.gender = gender
            email_obj.agent_position = agent_position
            email_obj.agent_email_address = agent_email_address
            email_obj.company_agent_surname = company_agent_surname
            email_obj.agent_academic_degree = agent_academic_degree
            email_obj.company_agent_first_name = company_first_name
            email_obj.tags = tags
            email_obj.save()
    else:
        form_delete_e = DeleteEmailForm
        form_delete_c = DeleteCompanyForm
        form_accept = CreateEmailForm
        form_update_e = UpdateEmailForm


    context = {
    'object': obj_company,
    'form_accept': form_accept,
    'form_update_e': form_update_e,
    'form_delete_c': form_delete_c,
    'form_delete_e': form_delete_e,
    'emails':emails,
    'tags':Tag.objects.all()
    }
    return render(request, template_name, context)


def detail_template_category(request, slug):
    category = get_object_or_404(CategoryTemplate, slug=slug)


    form_edit_template = EditTemplateForm(request.POST, request.FILES)
    if form_edit_template.is_valid():
        img = form_edit_template.cleaned_data.get("img")
        title = form_edit_template.cleaned_data.get("title")
        template = form_edit_template.cleaned_data.get("template")
        categories = form_edit_template.cleaned_data.get("categories")
        description = form_edit_template.cleaned_data.get("description")
        id_template = form_edit_template.cleaned_data.get("id_template")
        
        template_object = TemplateEmail.objects.get(id=id_template)
        
        if img:
            template_object.img = img
        if title:
            template_object.title = title
        if template:
            template_object.template = template
        if categories:
            category = CategoryTemplate.objects.get(id=categories)
            template_object.categories = category
        if description:
            template_object.description = description

        template_object.save()
            
        return redirect("email:template-category")

    form_delete_template = DeleteForm(request.POST)
    if form_delete_template.is_valid():
        id_template = form_delete_template.cleaned_data.get("id_template")
        id_template = int(id_template)
        template = TemplateEmail.objects.get(id=id_template)
        template.delete()

        return redirect("email:template-category")
        
        
    form_edit_template_category = EditTemplateCategoryForm(request.POST)
    if form_edit_template_category.is_valid():
        title = form_edit_template_category.cleaned_data.get("title")
        status = form_edit_template_category.cleaned_data.get("status")
        
        category.title = title
        category.status = status
        category.save()
        return redirect("email:template-category")
        
    context = {
        'category': category,
        'form_edit_template': form_edit_template,
        'form_delete_template': form_delete_template,
        'category_list': CategoryTemplate.objects.all(),
        'images': MemberProfile.objects.get(user=request.user),
        'form_edit_template_category': form_edit_template_category
    }
    return render(request, 'emails/detail-template-category.html', context)


def create_company(request):
    if request.user.is_superuser or request.user.adrole.create_company == True:
        template_name = 'emails/create-company.html'

        if request.method == 'POST':
            company_name = request.POST.get('company_name')
            state = request.POST.get('state')
            city = request.POST.get('city')
            street_number = request.POST.get('street_number')
            building_number = request.POST.get('building_number')
            unit = request.POST.get('unit')
            zip_code = request.POST.get('zip_code')
            size = request.POST.get('size')
            company_website_link = request.POST.get('company_website_link')
            country = request.POST.get('country')
            category = request.POST.get('category')
            fields = request.POST.get('fields')

            OutSrcs = request.POST.getlist('OutSrcs')
            services = request.POST.getlist('services')
            social_media = request.POST.getlist('social_media')
            products = request.POST.getlist('products')
            current_need = request.POST.getlist('current_need')
            future_need = request.POST.getlist('future_need')

            print('social_media', social_media)

            OutSrcs = str(OutSrcs)
            services = str(services)
            products = str(products)
            current_need = str(current_need)
            future_need = str(future_need)

            lst_horof = [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 
            'w', 'x', 'y', 'z','A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 
            'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',',', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'
            ]
            OutSrcs_str = ''
            for i in OutSrcs:
                if i in lst_horof:
                    OutSrcs_str += i
                    if i == ',':
                        OutSrcs_str += ' '

            services_str = ''
            for i in services:
                if i in lst_horof:
                    services_str += i
                    if i == ',':
                        services_str += ' '

            products_str = ''
            for i in products:
                if i in lst_horof:
                    products_str += i
                    if i == ',':
                        products_str += ' '

            current_need_str = ''
            for i in current_need:
                if i in lst_horof:
                    current_need_str += i
                    if i == ',':
                        current_need_str += ' '

            future_need_str = ''
            for i in future_need:
                if i in lst_horof:
                    future_need_str += i
                    if i == ',':
                        future_need_str += ' '
                        
            object_country = Country.objects.get(id=country)
            create_obj_company = Company.objects.create(
                company_name=company_name, state=state, city=city, 
                street_number=street_number, building_number=building_number, 
                country=object_country,unit=unit,size=size, 
                zip_code=zip_code, company_website_link=company_website_link, outsource=OutSrcs_str, creator=request.user,
                services=services_str, products=products_str, current_need=current_need_str, future_need=future_need_str,
                )
            messages.success(request, 'Company created successfully.')

            fields = fields.split(',')
            fields = set(fields)
            for i in fields:
                i = int(i)
                obj_cat = Category.objects.get(id=i)
                obj_cat.company = create_obj_company
                obj_cat.save()
                
            social_media = social_media[0]
            social_media = social_media.split(',')
            print('social_media', social_media)
            count_len = len(social_media) - 1
            first_count = 0
            last_count = 1
            for i in social_media:

                create_social_media = CompanySocialMedia.objects.create(
                    title=social_media[first_count], link=social_media[last_count], company=create_obj_company
                    )
                
                first_count += 2
                last_count += 2
                if count_len == last_count:
                    break
                
            # return redirect("email:create-category")
        context = {
            'category': Category.objects.all(),
            'country': Country.objects.all(),
        }

        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")



def create_institute(request):
    if request.user.is_superuser or request.user.adrole.create_institute == True:
        if request.method == 'POST':
            country = int(request.POST.get('country'))
            location = request.POST.get('location')
            web_address = request.POST.get('web_address')
            institute_name = request.POST.get('institute_name')

            create_institute = Institute.objects.create(
                institute_name=institute_name, country_id=country, location=location, 
                web_address=web_address, creator=request.user
                )
            messages.success(request, 'institute created successfully.')
            return redirect("email:create-institute")
        context = {
            'country': Country.objects.all(),          
        }
        return render(request, 'emails/create-institute.html', context)

    else:
        raise Http404("You can't see this page.")


class CreateCategoryTemplate(CreateCategoryTemplateMixin, CreatorMixnis, CreateView):
    model = CategoryTemplate
    success_url = reverse_lazy('email:create-category-template')
    template_name = 'emails/create-category-template.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = MemberProfile.objects.get(user=self.request.user)
        return context

class CreateCategory(CreateCategoryMixin, CreateView):
    model = Category
    success_url = reverse_lazy('email:create-category-new')
    template_name = 'emails/create-category.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = MemberProfile.objects.get(user=self.request.user)
        return context

class UploadImgCreate(UploadImgMixin, CreateView):
    model = UploadImg
    success_url = reverse_lazy('email:home')
    template_name = 'emails/upload-img.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = MemberProfile.objects.get(user=self.request.user)
        context['img'] = UploadImg.objects.all()
        return context


def create_template(request):
    if request.user.is_superuser or request.user.adrole.create_template == True:
        if request.method == 'POST':
            form = CreateForm(request.POST, request.FILES)
            if form.is_valid():
                img = form.cleaned_data.get("img")
                title = form.cleaned_data.get("title")
                template = form.cleaned_data.get("template")
                categories = form.cleaned_data.get("categories")
                description = form.cleaned_data.get("description")

                category = CategoryTemplate.objects.get(id=categories)

                create = TemplateEmail.objects.create(
                    description=description, title=title, img=img, 
                    template=template, categories=category, creator=request.user
                    )

                # with open('/home/tecvicoc/public_html/media/email/template/{}'.format(template), 'r') as f1, open('/home/tecvicoc/ivc/email_app/templates/emails/email/{}'.format(template), 'w') as f2:
                with open('media/email/template/{}'.format(template), 'r') as f1, open('email_app/templates/emails/email/{}'.format(template), 'w') as f2:
                    for i in f1:
                        print(i)
                        f2.write(i)
                # #   f2.write('salamm')




                return redirect("email:create-template")
        else:
            form = CreateForm
        context = {
        "form": form,
        "category": CategoryTemplate.objects.all()
        }

        return render(request, 'emails/create-template.html', context)
    else:
        raise Http404("You can't see this page.")

def send_email(request):
    if request.user.is_superuser or request.user.adrole.send_email == True:
        images = MemberProfile.objects.get(user=request.user)
        categories = Company.objects.Active()
        count = 0
        today = date.today().strftime("%Y-%m-%d 00:00:00+00:00")
        reminder_list=[]
        reminders=ReminderEmails.objects.filter(user=request.user).all()
        for reminder in reminders:
            if str(reminder.send_date)==str(today):
                emaillist=reminder.emaillist
                emaillist = emaillist.split(",")
                reminder.emaillist=emaillist
                reminder_list.append(reminder)

        # if request.method == 'POST':
        #     text = request.POST.get('text')
        #     position = request.POST.get('position')
        #     subject = request.POST.get('subject')
        #     Cemail_list = request.POST.get('Cemail_list')
        #     email_list = request.POST.getlist('email_list[]')
        #     print(text)
        #     print(position)
        #     print(str(subject))
        #     print(Cemail_list)
        #     print(email_list)
        #     new_history_email = HistorySendEmail.objects.create(user=request.user, text=text, subject=subject)

        #     text = text.split(' ')
        #     for e in email_list:
        #         if position == "institute":
        #             email_obj = EmailsInstitute.objects.get(email_address=e)

        #             message_email = ''
        #             for i in text:
        #                 if i =='<!name!>':
        #                     if email_obj.degree == 'Doctoral degree':
        #                         message_email += 'Dr. {}'.format(email_obj.full_name)
        #                         message_email += ' '
        #                     else:
        #                         if  email_obj.gender == 'Male':
        #                             message_email += 'Mr. {}'.format(email_obj.full_name)
        #                             message_email += ' '
        #                         else:
        #                             message_email += 'Ms. {}'.format(email_obj.full_name)
        #                             message_email += ' '
        #                 else:
        #                     message_email += i
        #                     message_email += ' '

        #         elif position == "workshop":
        #             email_obj = User.objects.get(email=e)

        #             message_email = ''
        #             for i in text:
        #                 if i =='<!name!>':
        #                     if email_obj.user.memberprofile.degree == 'Doctoral degree':
        #                         message_email += 'Dr. {}'.format(email_obj.user.get_full_name())
        #                         message_email += ' '
        #                     else:
        #                         if  email_obj.user.memberprofile.gender == 'Male':
        #                             message_email += 'Mr. {}'.format(email_obj.user.get_full_name())
        #                             message_email += ' '
        #                         else:
        #                             message_email += 'Ms. {}'.format(email_obj.user.get_full_name())
        #                             message_email += ' '
        #                 else:
        #                     message_email += i
        #                     message_email += ' '

        #         elif position == "company":
        #             email_obj = Emails.objects.get(agent_email_address=e)

        #             message_email = ''
        #             for i in text:
        #                 if i =='<!name!>':
        #                     if email_obj.agent_academic_degree == 'Doctoral degree':
        #                         message_email += 'Dr. {}'.format(email_obj.company_agent_surname)
        #                         message_email += ' '
        #                     else:
        #                         if email_obj.gender == 'Male':
        #                             message_email += 'Mr. {}'.format(email_obj.company_agent_surname)
        #                             message_email += ' '
        #                         else:
        #                             message_email += 'Ms. {}'.format(email_obj.company_agent_surname)
        #                             message_email += ' '
        #                 else:
        #                     message_email += i
        #                     message_email += ' '

        #         email_history = SendEmail.objects.create(email=e, history=new_history_email)

        #         subject = subject
        #         message = message_email
        #         recepient = [e]
        #         send_mail(subject, 
        #             message, Cemail_list, recepient, fail_silently = False)
        #         count += 1
                    

        #         from_email=settings.DEFAULTE_HOST_USER

        #         email_history.sent = True
        #         email_history.save()

                        


        context = {
            "categories": categories,
            'workshops' : Workshop.objects.filter(status='Accept'),
            'institutes': Institute.objects.filter(status='visible').order_by("-created"),
            # 'institutes': Institute.objects.all().order_by("-created"),
            'count': count,
            'images': images,
            'reminder_list':reminder_list,
            'departments':DepartmentInstitu.objects.filter(approove=True).all(),
            'users_workshop':Users_Workshops.objects.filter(is_paid=True)
        }
        return render(request, 'emails/send-email.html',context)

    else:
        raise Http404("You can't see this page.")
            

def send_email_template(request):
    if request.user.is_superuser or request.user.adrole.send_email_template == True:
        categories_template = CategoryTemplate.objects.all()
        templates = TemplateEmail.objects.all()
            
        # if request.method == 'POST':
        #     email_list = request.POST.getlist('email_list[]')
        #     templateid = request.POST.get('templateId')
        #     subject = request.POST.get('subject')
        #     Cemail_list = request.POST.get('Cemail_list')

        #     templateid = int(templateid)
        #     template = TemplateEmail.objects.get(id=templateid)
        #     x = template.template
        #     x = str(x)
        #     z = x.split('template/')
        #     c = z[1]
        #     new_send_email = HistorySendEmail.objects.create(user=request.user, template_name=c, text='template', categories=email_list, subject=subject)
            
        #     for i in email_list:
        #         message = EmailMultiAlternatives(subject=subject, body='', from_email=Cemail_list, to=[i])
        #         html_template = get_template("emails/email/{}".format(c)).render()
        #         message.attach_alternative(html_template, "text/html")
        #         message.send()
        #     return redirect("email:home")


        context = {
            'categories_template' : CategoryTemplate.objects.all(),
            'templates' : templates,
            'workshops' : Workshop.objects.filter(status='Accept'),
            'institutes': Institute.objects.filter(status='visible').order_by("-created"),
            'copanys' : Company.objects.Active(),
            'users_workshop':Users_Workshops.objects.filter(is_paid=True)
        }
        return render(request, 'emails/send-email-template.html', context)
    else:
        raise Http404("You can't see this page.")

def select_template(request):
    context = {
        'templates' : TemplateEmail.objects.all(),
    }
    return render(request, 'emails/template-select.html', context)

def detail_select_template(request, pk):
    template = TemplateEmail.objects.get(id=pk)

    description = ''
    form = EmailRasouliForm(request.POST, request.FILES)
    if form.is_valid():
        subject = form.cleaned_data.get("subject")
        email_list = request.POST.getlist('email_list[]')
        description = form.cleaned_data.get("description")
        Cemail_list = request.POST.get('Cemail_list')
        position = request.POST.get('position')

        
        template_addres = template.template
        template_addres = str(template_addres)
        template_list = template_addres.split('template/')
        template_name = template_list[1]

        new_send_email = HistorySendEmail.objects.create(user=request.user, template_name=template_name, text='template', categories=email_list, subject=subject)


        text = description.split(' ')
        for e in email_list:

            if position == "institute":
                email_obj = EmailsInstitute.objects.get(email_address=e)

                message_email = ''
                for i in text:
                    if i =='<!name!>':
                        if email_obj.degree == 'Doctoral degree':
                            message_email += 'Dr. {}'.format(email_obj.full_name)
                            message_email += ' '
                        else:
                            if  email_obj.gender == 'Male':
                                message_email += 'Mr. {}'.format(email_obj.full_name)
                                message_email += ' '
                            else:
                                message_email += 'Ms. {}'.format(email_obj.full_name)
                                message_email += ' '
                    else:
                        message_email += i
                        message_email += ' '


            elif position == "workshop":
                email_obj = User.objects.get(email=e)

                message_email = ''
                for i in text:
                    if i =='<!name!>':
                        if email_obj.user.memberprofile.degree == 'Doctoral degree':
                            message_email += 'Dr. {}'.format(email_obj.user.get_full_name())
                            message_email += ' '
                        else:
                            if  email_obj.user.memberprofile.gender == 'Male':
                                message_email += 'Mr. {}'.format(email_obj.user.get_full_name())
                                message_email += ' '
                            else:
                                message_email += 'Ms. {}'.format(email_obj.user.get_full_name())
                                message_email += ' '
                    else:
                        message_email += i
                        message_email += ' '

            elif position == "company":
                email_obj = Emails.objects.get(agent_email_address=e)

                message_email = ''
                for i in text:
                    if i =='<!name!>':
                        if email_obj.agent_academic_degree == 'Doctoral degree':
                            message_email += 'Dr. {}'.format(email_obj.company_agent_surname)
                            message_email += ' '
                        else:
                            if email_obj.gender == 'Male':
                                message_email += 'Mr. {}'.format(email_obj.company_agent_surname)
                                message_email += ' '
                            else:
                                message_email += 'Ms. {}'.format(email_obj.company_agent_surname)
                                message_email += ' '
                    else:
                        message_email += i
                        message_email += ' '


            context = {
                'body_message' : message_email,
            }

            html_body = render_to_string("emails/email/{}".format(template_name), context)
            #e_content = "Dear {user}\nHi\nHope you are going well.\nYou paid {cost} at {date}\n{intent} \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company:\nEmail: payment@tecvico.com\n\nThank you.\n\nBest regards\n\n".format(user = instance.user, cost = instance.purchased_amount, date = instance.date_created, intent = instance.payment_intent)
            msg = EmailMultiAlternatives(subject=subject, from_email=Cemail_list,to=[e], body='')
            msg.attach_alternative(html_body, "text/html")
            msg.send()



    form_project = EmailProject(request.POST, request.FILES)
    if form_project.is_valid():
        title = form_project.cleaned_data.get("title")
        projectlink = form_project.cleaned_data.get("projectlink")
        img = form_project.cleaned_data.get("img")
        description = form_project.cleaned_data.get("description")

        if img != None and description != None:
            create_project = SendEmailProject.objects.create(img=img, description=description,title=title,projectlink=projectlink)
            projects=SendEmailProject.objects.all()
            context={
                'projects':projects
            }
            #html_body = render_to_string("emails/email/test.html", context=context)
    if 'mail.html' in str(template.template):
        form_mode='project'
    else:
        form_mode='notprojects'

    context = {
        'form': form,
        'object': template,
        'form_project': form_project,
        'workshops' : Workshop.objects.filter(status='Accept'),
        'body_message' : description,
        'institutes': Institute.objects.filter(status='visible').order_by("-created"),
        'projects': SendEmailProject.objects.all(),
        'copanys' : Company.objects.Active(),
        'form_mode':form_mode,
        'users_workshop':Users_Workshops.objects.filter(is_paid=True)
    }


    return render(request, 'emails/send-template-primary.html', context)



def send_research_project_template(request):
    id=request.GET.get('id')
    
    if request.method == 'POST':
        email_list = request.POST.getlist('email_list[]')
        Cemail_list = request.POST.get('Cemail_list')
        subject = request.POST.get('subject')
        
        return HttpResponse('dwadwadwa')


        context = {
            'projects': SendEmailProject.objects.all()
        }


        html_body = render_to_string("emails/email/mail.html", context)
        #e_content = "Dear {user}\nHi\nHope you are going well.\nYou paid {cost} at {date}\n{intent} \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company:\nEmail: payment@tecvico.com\n\nThank you.\n\nBest regards\n\n".format(user = instance.user, cost = instance.purchased_amount, date = instance.date_created, intent = instance.payment_intent)
        msg = EmailMultiAlternatives(subject=subject, from_email=Cemail_list, to=email_list, body='')
        msg.attach_alternative(html_body, "text/html")
        msg.send()

        return redirect("email:home")
    context = {
        'projects': SendEmailProject.objects.all(),
        'copanys' : Company.objects.Active(),
        'workshops' : Workshop.objects.filter(status='Accept'),
        'institutes': Institute.objects.filter(status='visible').order_by("-created"),
        'id':id,
        'users_workshop':Users_Workshops.objects.filter(is_paid=True)
    }
    return render(request, 'emails/send-email-research-template.html', context)


class DeleteProjectsEmail( DeleteView):
    model = SendEmailProject
    success_url = reverse_lazy('email:home') 
    template_name = 'emails/delete-projects.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = MemberProfile.objects.get(user=self.request.user)
        return context

class History(ListView):
    template_name = 'emails/history.html'
    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.has_perm('email_app.view_category'):
            return HistorySendEmail.objects.all().order_by('-created')
        else:
            raise Http404("You can't see this page.")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = MemberProfile.objects.get(user=self.request.user)
        context['categories'] = Company.objects.Active()
        return context


# #Delete, Update
# class DeleteEmail(DeleteMixins, DeleteView):
#     model = Emails
#     success_url = reverse_lazy('email:home') 
#     template_name = 'emails/delete-email.html'
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['images'] = MemberProfile.objects.get(user=self.request.user)
#         return context


# class DeleteCategory(DeleteMixins, DeleteView):
#     model = Company
#     success_url = reverse_lazy('email:home') 
#     template_name = 'emails/delete-category.html'
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['images'] = MemberProfile.objects.get(user=self.request.user)
#         return context


class UpdateEmail(UpdateEmailMixin, UpdateMixnis, UpdateView):
    model = Emails
    success_url = reverse_lazy('email:home')
    template_name = 'emails/create-email.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = MemberProfile.objects.get(user=self.request.user)
        context['tags']=Tag.objects.all()
        return context


class UpdateCompany(CreateCompanyMixin, UpdateMixnis, UpdateView):
    model = Company
    success_url = reverse_lazy('email:home')
    template_name = 'emails/update-company.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = MemberProfile.objects.get(user=self.request.user)
        return context

def WorkshopListView(request):
    workshop = Workshop.objects.filter(status="Accept")
    for w in workshop:
        timetabel=TimeTable.objects.filter(workshop=w).first()
        w.date_event=timetabel.start_date
    context = {
        "workshops":workshop,
    }
    return render(request,"emails/workshop_title.html",context)
    
class ResearchListAd(ListView):
    paginate_by = 20
    template_name = "emails/research_title.html"
    def get_queryset(self):
        return ResearchProject.objects.filter(status__in=["new", "on_going", "done"]).order_by("-created")
    
    






# lotfi.........................
def send_email_test(request):
    if (request.method == 'POST'):
        text = request.POST.get('text')
        new_history_email_id = request.POST.get('new_history_email_id')
        position = request.POST.get('position')
        
        subject = request.POST.get('subject')
        Cemail_list = request.POST.get('Cemail_list')
        e = request.POST.getlist('email_list')[0]
        history=request.POST.get('history')
        command=request.POST.get('command')
        if new_history_email_id =='create':
            new_history_email=HistorySendEmail.objects.create(user=request.user,text=str(text), subject=str(subject))

        else:
            new_history_email=HistorySendEmail.objects.filter(id=new_history_email_id,user=request.user, text=text, subject=str(subject)).first()

        email_history = SendEmail.objects.create(email=e, history=new_history_email,sent=False)
        text = text.split(' ')
        if position == "institute":
            email_obj = EmailsInstitute.objects.filter(email_address=e).first()

            message_email = ''
            for i in text:
                if i =='<!name!>':
                    if email_obj.degree == 'Doctoral degree':
                        message_email += 'Dr. {}'.format(email_obj.full_name)
                        message_email += ' '
                    else:
                        if  email_obj.gender == 'Male':
                            message_email += 'Mr. {}'.format(email_obj.full_name)
                            message_email += ' '
                        else:
                            message_email += 'Ms. {}'.format(email_obj.full_name)
                            message_email += ' '
                else:
                    message_email += i
                    message_email += ' '

        elif position == "workshop":
            email_obj = User.objects.filter(email=e).first()

            message_email = ''
            for i in text:
                if i =='<!name!>':
                    if email_obj.user.memberprofile.degree == 'Doctoral degree':
                        message_email += 'Dr. {}'.format(email_obj.user.get_full_name())
                        message_email += ' '
                    else:
                        if  email_obj.user.memberprofile.gender == 'Male':
                            message_email += 'Mr. {}'.format(email_obj.user.get_full_name())
                            message_email += ' '
                        else:
                            message_email += 'Ms. {}'.format(email_obj.user.get_full_name())
                            message_email += ' '
                else:
                    message_email += i
                    message_email += ' '

        elif position == "company":
            email_obj = Emails.objects.filter(agent_email_address=e).first()

            message_email = ''
            for i in text:
                if i =='<!name!>':
                    if email_obj.agent_academic_degree == 'Doctoral degree':
                        message_email += 'Dr. {}'.format(email_obj.company_agent_surname)
                        message_email += ' '
                    else:
                        if email_obj.gender == 'Male':
                            message_email += 'Mr. {}'.format(email_obj.company_agent_surname)
                            message_email += ' '
                        else:
                            message_email += 'Ms. {}'.format(email_obj.company_agent_surname)
                            message_email += ' '
                else:
                    message_email += i
                    message_email += ' '

        message = message_email
        recepient = [e]
        result=send_mail(subject, 
            message, Cemail_list, recepient, fail_silently = True)
        from_email=settings.DEFAULTE_HOST_USER
        email_history.sent = result
        email_history.save()

        response=({'result':result,'new_history_email_id':new_history_email.id})
    return JsonResponse(response)



def send_email_template_test(request):
  if request.method == 'POST':
        new_history_email_id = request.POST.get('new_history_email_id')
        email_list = request.POST.getlist('email_list')
        templateid = request.POST.get('templateId')
        subject = request.POST.get('subject')
        Cemail_list = request.POST.get('Cemail_list')
        

        templateid = int(templateid)
        template = TemplateEmail.objects.get(id=templateid)
        if template.categories.title == 'primary':
            if 'mail.html' in str(template.template):
                projects=SendEmailProject.objects.all()
                context={
                    'projects':projects
                }
            else:
                img=template.img
                print(request.POST.get('description'))
                context={
                    'description':request.POST.get('description')
                }
            
        else:
            img=template.img
            context={
                'description':img
            }
            
            print('projects')
        x = template.template
        x = str(x)
        z = x.split('template/')
        c = z[1]

        if new_history_email_id =='create':
            new_history_email=HistorySendEmail.objects.create(user=request.user, template_name=c, text='template', subject=subject)

        else:
            new_history_email=HistorySendEmail.objects.filter(id=new_history_email_id,user=request.user, template_name=c, text='template', subject=subject).first()
        

        for e in email_list:

            email_history = SendEmail.objects.create(email=e, history=new_history_email,sent=False)
            message = EmailMultiAlternatives(subject=subject, body='', from_email=Cemail_list, to=[e])
            # html_1template = get_template("emails/email/{}".format(c))
            html_1template=render_to_string("emails/email/{}".format(c),context)
            message.attach_alternative(html_1template, "text/html")
            message.send()
            email_history.sent=True
            email_history.save()
        # return redirect("email:home")        
          
        response=({'result':True,'new_history_email_id':new_history_email.id})
  return JsonResponse(response)




def show_last_history(request):
    if request.method == 'POST':
        history_email=HistorySendEmail.objects.filter(user=request.user).last()
        # history_email=history_email[len(history_email)]
        if history_email is not None:
            total_emails=SendEmail.objects.filter(history=history_email).all()
            successful=SendEmail.objects.filter(history=history_email,sent=True).all()
            failed=SendEmail.objects.filter(history=history_email,sent=False).all()
            created=history_email.created
            subject=history_email.subject
            failed_emailes=[]
            for failed_email in failed:
                failed_emailes.append(failed_email.email)
        
            
            response=({
                'data':'true',
                'created':created,
                'total_email':len(total_emails),
                'subject':subject,
                'successful':len(successful),
                'failed':len(failed),
                'failed_emailes':failed_emailes
                })
        else:
          response=({
                'data':'false',
          })  
    return JsonResponse(response)
         


def get_email_details(request):
    if (request.method == 'POST'):
        position=request.POST.get('position')
        email=request.POST.get('email')
        if position == "company":
            failed_email=Emails.objects.filter(agent_email_address=email)
            failed_email=serializers.serialize("json", failed_email)
        elif position=='institute':
            failed_email=EmailsInstitute.objects.filter(email_address=email)
            failed_email=serializers.serialize("json", failed_email)
        elif position=='workshop':
            pass
        response=({'failed_email':failed_email})
    return JsonResponse(response)



def check_email(request):
    if (request.method == 'POST'):
        agent_email_address=request.POST.get('email_name')
        already_exist=Emails.objects.filter(agent_email_address=agent_email_address).all()
        if  len(already_exist)==0:
            result=True
        else:
            result=False
        print(result)
        response=({'result':result})
    return JsonResponse(response)


def check_email_institute(request):
    if (request.method == 'POST'):
        agent_email_address=request.POST.get('email_name')
        already_exist=EmailsInstitute.objects.filter(email_address=agent_email_address).all()
        if  len(already_exist)==0:
            result=True
        else:
            result=False
        print(result)
        response=({'result':result})
    return JsonResponse(response)

  

def create_reminder(request):
    if (request.method == 'POST'):
        data=request.POST.get('data')
        email_list=request.POST.getlist('email_list[]')
        subject=request.POST.get('subject')
        text=request.POST.get('text')
        csrf,date=data.split('&')
        date=date.split('=')[1]
        email=','.join(email_list)
        new_reminder=ReminderEmails.objects.create(
            subject=subject,
            text=text,
            send_date=date,
            emaillist=email,
            user=request.user
        )
        if new_reminder:
            result=True
        else:
            result=False
        response=({'result':result})
    return JsonResponse(response)

def email_notif(request):
    if (request.method == 'POST'):
        # send_email
        today = date.today().strftime("%Y-%m-%d 00:00:00+00:00")
        notif_send_email=0
        reminders=ReminderEmails.objects.filter(user=request.user).all()
        for reminder in reminders:
            if str(reminder.send_date)==str(today):
                notif_send_email=notif_send_email+1

        response=({'notif_send_email':notif_send_email})
    return JsonResponse(response)


def create_new_department(request):
    if request.method == 'POST':
        departmentslist=request.POST.getlist('departments[]')
        departments_path = os.path.join(os.path.dirname(__file__), 'departments.txt')
        departments = open(departments_path , 'a+')
        for department in departmentslist:
            departments.write(department)
            departments.write("\n")
            # create_department=DepartmentInstitu.objects.create(name=department,user=request.user,approove=False)          
        departments.close()
        
        response=({'res':True})
    return JsonResponse(response)


def email_director(request):
    departments_path = os.path.join(os.path.dirname(__file__), 'departments.txt')
    readdepartments = open(departments_path , 'a+')
    readdepartments.seek(0)
    readdepartments=readdepartments.readlines()
    departments=[]
    for i in readdepartments:
        if not i.strip():
           continue
        if i:
            department_exist=DepartmentInstitu.objects.filter(name=i).first()
            if department_exist is None:
               new_department=DepartmentInstitu.objects.create(user=request.user,name=i,approove=False)
    not_approve=DepartmentInstitu.objects.filter(approove=False,viwed=False).all()
    departments=DepartmentInstitu.objects.filter(approove=True).all()

    context={
        'departments':departments,
        'not_approve':not_approve
    }

    return render (request,'emails/director.html',context)



def update_department(request):
    if request.method=="POST":
        id=request.POST.get('id')
        command=request.POST.get('command')
        print(command)
        if command=='approve':
            
            department=DepartmentInstitu.objects.filter(id=id).first()
            department.approove=True
            department.save()
            result=True
            command='add'
        else:    
            departmentname=DepartmentInstitu.objects.filter(id=id).first()
            departmentname.viwed=True
            departmentname.save()
            # departmentname=departmentname.name
            # departments_path = os.path.join(os.path.dirname(__file__), 'departments.txt')
            # readdepartments = open(departments_path , 'r')
            # writepartments = open(departments_path , 'w')
            # lines = readdepartments.readlines()
            # i=0
            # for line in lines:             
            #     i=i+1
            #     if line != departmentname:
            #         lines[i]=line
            #     else:
            #         lines[i]=''
            # for line in lines:
            #     writepartments.write(line)
            #     writepartments.write('\n')
            # readdepartments.close()
            command="delete"
            result=True


        response=({'command':command,'id':id,'result':result})
    return JsonResponse(response)



def ajax_filtering_email_company(request):
    template_name='emails/filtering.html'
    position=request.POST.get('position')
    result=[]
    value=request.POST.get('value').split(',')
    if value[0] == '':
        pass
    else:
        for item in value:  
            if position == 'company':
                emails=Emails.objects.filter(tags__icontains=item)
            elif position == 'institute':
                emails=EmailsInstitute.objects.filter(tags__icontains=item)            
            for email in emails:
                tags=email.tags.split(',')
                for tag in tags:
                    if tag == item:
                        result.append(email)
                        break
    context={
        'emails':list(dict.fromkeys(result)),
        'position':position
    }

    return render(request,template_name,context)





def create_tag(request):
    template_name='emails/create_tag.html'
    if request.GET.get('edit'):
        pk=request.GET.get('edit')
        object=get_object_or_404(Tag,pk=pk)
        context={'object':object}
        if request.method=="POST":
            name=request.POST.get('name')
            description=request.POST.get('description')
            object.name=name
            object.description=description
            object.save()
            messages.success(request,'Tag has been edited')
            return redirect('../emails?filter=home/tags')
    elif request.GET.get('delete'):
        pk=request.GET.get('delete')
        object=get_object_or_404(Tag,pk=pk)
        object.delete()
        messages.error(request,'Tag has been deleted')
        return redirect('../emails?filter=home/tags')
    else:
         context={}
         if request.method=="POST":
            name=request.POST.get('name')
            description=request.POST.get('description')
            Tag.objects.create(name=name,description=description)
            messages.success(request,'Tag has been created')
            return redirect('../emails?filter=home/tags')
    
        
    return render(request,template_name,context)

