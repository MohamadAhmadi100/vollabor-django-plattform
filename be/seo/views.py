from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db.models import Q

from seo.forms import RobotsForm, TitleDescriptionForm
from seo.models import *
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from datetime import date
from research.models import RequestUserForProject, ResearchProject

from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
import datetime
import time
from datetime import date, timedelta
@login_required
def robots(request):
    #if SEO.objects.filter(user=request.user).count() == 0:
    #    return render(request, 'ivc_website/403.html')

    robot_form = RobotsForm()
    if request.method == "POST":
        if 'delete-tag' in request.POST:
            tag_pk = request.POST['delete-tag']
            RobotsMeta.objects.get(pk=tag_pk).delete()

            messages.success(request, "Tag has been deleted successfully")
            return HttpResponseRedirect(request.path_info)  # redirect to the same page
        else:
            robot_form = RobotsForm(request.POST)
            if robot_form.is_valid():
                robot_form.save()
                messages.success(request, "Meta tag has been added successfully")
                return HttpResponseRedirect(request.path_info)  # redirect to the same page
            else:
                messages.error(request, "An error is occurred")

    paginator = Paginator(RobotsMeta.objects.all(), 20)
    current_page_number = request.GET.get('page')
    page_obj = paginator.get_page(current_page_number)

    context = {
        'new_form': robot_form,
        'current_tags': page_obj
    }
    return render(request, 'seo/robots_meta.html', context=context)


@login_required
def title_and_description(request):
    title_description_form = TitleDescriptionForm()

    if request.method == "POST":
        title_description_form = TitleDescriptionForm(request.POST)
        if title_description_form.is_valid():
            title_description_form.save()
            messages.success(request, "Meta tag has been added successfully")
            return redirect('metatag-page')  # redirect to the same page
        else:
            messages.error(request, title_description_form.errors)
            return HttpResponseRedirect(request.path_info)  # redirect to the same page

    context = {
        'new_form': title_description_form,
    }
    return render(request, 'seo/title_description_meta.html', context=context)
    
    
@login_required
def title_and_description_update(request, pk):
    form = TitleAndDescription.objects.get(pk = pk)
    if request.method == "POST":
        title_description_form = TitleDescriptionForm(request.POST, instance=form)
        if title_description_form.is_valid():
            title_description_form.save()
            messages.success(request, "Meta tag has been updated successfully")
            return redirect('metatag-page')  # redirect to the same page
        else:
            messages.error(request, title_description_form.errors)
            return HttpResponseRedirect(request.path_info)  # redirect to the same page
    elif request.method == "GET":
        title_description_form = TitleDescriptionForm(instance=form)
        context = {
            'new_form': title_description_form,
        }
        return render(request, 'seo/title_description_meta.html', context=context)

@login_required
def metatag_list(request):
    if request.method == 'GET':
        paginator = Paginator(TitleAndDescription.objects.all(), 10)
        current_page_number = request.GET.get('page')
        page_obj = paginator.get_page(current_page_number)

        context = {
            'current_tags': page_obj
        }
        return render(request, 'seo/meta_list.html', context=context)
    elif request.method == 'POST':
        tag_pk = request.POST['delete-tag']
        TitleAndDescription.objects.get(pk=tag_pk).delete()

        messages.error(request, "Tag has been deleted successfully")
        return HttpResponseRedirect(request.path_info)  # redirect to the same page

def user_footprint(request):
    context = {
        'users': User.objects.all(),
        'projects': ResearchProject.objects.filter(~Q(status="delete")),
    }
    return render(request, 'seo/user_footprint.html', context=context)


def user_footprint_ajax(request):
    if request.method == 'POST':
        global select_box
        global start_date
        global end_date
        global position
        select_box = request.POST.get('select_box')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        position = request.POST.get('position')


        context = {}
        obj_list = []
        register_users = []
        users_footprint = []
        count_obj = 0
        count_detail = 0

        count_home_forum = 0
        count_topic_forum = 0
        count_subcategory_forum = 0
        count_subcategory_list_forum = 0
        objs = UserFootprint.objects.all().order_by('-created')
        applicants = RequestUserForProject.objects.filter(~Q(status__in=["is_change", "not-pay"]),).order_by('-created')
        users = User.objects.all()
        projects = ResearchProject.objects.filter(~Q(status="delete"))

        all_applicant = 0
        applay_applicant = 0
        accept_applicant = 0
        reject_applicant = 0
        if position == 'select_user':
            if start_date == '' and end_date == '':
                users_footprint = UserFootprint.objects.filter(user_id=select_box).order_by('-created')


            elif start_date != '' and end_date != '':
                for i in objs:
                    created_obj = str(i.created)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]

                    if start_date <= created_obj and end_date >= created_obj:
                        users_footprint.append(i)

            elif start_date != '':
                for i in objs:
                    created_obj = str(i.created)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]

                    if start_date <= created_obj:
                        users_footprint.append(i)

            elif end_date != '':
                for i in objs:
                    created_obj = str(i.created)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]

                    if end_date >= created_obj:
                        users_footprint.append(i)

        elif position == 'select_url':
            if start_date == '' and end_date == '':
                if select_box == '/blog/':
                    for i in objs:
                        if i.url == '/blog/':
                            count_obj += 1
                        elif '/blog/detail/' in i.url:
                            count_detail += 1
                        if '/blog/' in i.url:
                            users_footprint.append(i)
                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/news/':
                    for i in objs:
                        if i.url == '/news/':
                            count_obj += 1
                        elif '/news_detail/' in i.url:
                            count_detail += 1
                        if '/news/' in i.url or '/news_detail/' in i.url:
                            users_footprint.append(i)
                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/videos/':
                    for i in objs:
                        if i.url == '/videos/':
                            count_obj += 1
                        elif '/videos/detail/' in i.url:
                            count_detail += 1
                        if '/videos/' in i.url:
                            users_footprint.append(i)
                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/forum/':
                    for i in objs:
                        if i.url == '/forum/':
                            count_home_forum += 1

                        elif '/forum/category/' in i.url:
                            count_subcategory_forum += 1

                        elif '/forum/sub-category/topic/' in i.url:
                            count_subcategory_list_forum += 1

                        elif '/forum/topic/' in i.url:
                            count_topic_forum += 1


                        if '/forum/' in i.url:
                            users_footprint.append(i)
                    context['count_home_forum'] = count_home_forum
                    context['count_topic_forum'] = count_topic_forum
                    context['count_subcategory_forum'] = count_subcategory_forum
                    context['count_subcategory_list_forum'] = count_subcategory_list_forum

                elif select_box == '/projects/':
                    for i in objs:
                        if i.url == '/projects/':
                            count_obj += 1
                        elif 'project/detail/' in i.url:
                            count_detail += 1
                        if '/projects/' in i.url or '/project/detail/' in i.url:
                            users_footprint.append(i)
                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/dashboard/projects':
                    for i in objs:
                        if i.url == '/dashboard/projects':
                            count_obj += 1
                        elif '/dashboard/project/detail/' in i.url:
                            count_detail += 1
                        if i.url == '/dashboard/projects' or '/dashboard/project/detail/' in i.url:
                            users_footprint.append(i)
                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/workshop/list-for-all/':
                    for i in objs:
                        if i.url == '/workshop/list-for-all/':
                            count_obj += 1
                        elif '/workshop/view-workshop/' in i.url:
                            count_detail += 1
                        if i.url == '/workshop/list-for-all/' or '/workshop/view-workshop/' in i.url:
                            users_footprint.append(i)
                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                else:
                    users_footprint = UserFootprint.objects.filter(url=select_box).order_by('-created')


            elif start_date != '' and end_date != '':
                if select_box == '/blog/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if start_date <= created_obj and end_date >= created_obj:
                            obj_list.append(i)

                    for i in obj_list:
                        if i.url == '/blog/':
                            count_obj += 1
                        elif '/blog/detail/' in i.url:
                            count_detail += 1
                        if '/blog/' in i.url:
                            users_footprint.append(i)

                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/news/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]
                        if start_date <= created_obj and end_date >= created_obj:
                            obj_list.append(i)

                    for i in obj_list:
                        if i.url == '/news/':
                            count_obj += 1
                        elif '/news_detail/' in i.url:
                            count_detail += 1
                        if '/news/' in i.url or '/news_detail/' in i.url:
                            users_footprint.append(i)

                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/videos/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]
                        if start_date <= created_obj and end_date >= created_obj:
                            obj_list.append(i)

                    for i in obj_list:
                        if i.url == '/videos/':
                            count_obj += 1
                        elif '/videos/detail/' in i.url:
                            count_detail += 1
                        if '/videos/' in i.url:
                            users_footprint.append(i)

                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/forum/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]
                        if start_date <= created_obj and end_date >= created_obj:
                            obj_list.append(i)

                    for i in obj_list:
                        if i.url == '/forum/':
                            count_home_forum += 1

                        elif '/forum/category/' in i.url:
                            count_subcategory_forum += 1

                        elif '/forum/sub-category/topic/' in i.url:
                            count_subcategory_list_forum += 1

                        elif '/forum/topic/' in i.url:
                            count_topic_forum += 1


                        if '/forum/' in i.url:
                            users_footprint.append(i)
                    context['count_home_forum'] = count_home_forum
                    context['count_topic_forum'] = count_topic_forum
                    context['count_subcategory_forum'] = count_subcategory_forum
                    context['count_subcategory_list_forum'] = count_subcategory_list_forum


                elif select_box == '/projects/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]
                        if start_date <= created_obj and end_date >= created_obj:
                            obj_list.append(i)

                    for i in obj_list:
                        if i.url == '/projects/':
                            count_obj += 1
                        elif 'project/detail/' in i.url:
                            count_detail += 1
                        if '/projects/' in i.url or '/project/detail/' in i.url:
                            users_footprint.append(i)
                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/dashboard/projects':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]
                        if start_date <= created_obj and end_date >= created_obj:
                            obj_list.append(i)

                    for i in obj_list:
                        if i.url == '/dashboard/projects':
                            count_obj += 1
                        elif '/dashboard/project/detail/' in i.url:
                            count_detail += 1
                        if '/dashboard/projects' in i.url or '/dashboard/project/detail/' in i.url:
                            users_footprint.append(i)
                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/workshop/list-for-all/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]
                        if start_date <= created_obj and end_date >= created_obj:
                            obj_list.append(i)

                    for i in obj_list:
                        if i.url == '/workshop/list-for-all/':
                            count_obj += 1
                        elif '/workshop/view-workshop/' in i.url:
                            count_detail += 1
                        if '/workshop/list-for-all/' in i.url or '/workshop/view-workshop/' in i.url:
                            users_footprint.append(i)
                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail
                else:
                    users_footprint = []
                    objs = UserFootprint.objects.filter(url=select_box).order_by('-created')
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if start_date <= created_obj and end_date >= created_obj:
                            users_footprint.append(i)


            elif start_date != '':
                if select_box == '/blog/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if start_date <= created_obj:
                            obj_list.append(i)

                    for i in obj_list:
                        if i.url == '/blog/':
                            count_obj += 1
                        elif '/blog/detail/' in i.url:
                            count_detail += 1
                        if '/blog/' in i.url:
                            users_footprint.append(i)

                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/news/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if start_date <= created_obj:
                            obj_list.append(i)

                    for i in obj_list:
                        if i.url == '/news/':
                            count_obj += 1
                        elif '/news_detail/' in i.url:
                            count_detail += 1
                        if '/news/' in i.url or '/news_detail/' in i.url:
                            users_footprint.append(i)

                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/videos/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if start_date <= created_obj:
                            obj_list.append(i)

                    for i in obj_list:
                        if i.url == '/videos/':
                            count_obj += 1
                        elif '/videos/detail/' in i.url:
                            count_detail += 1
                        if '/videos/' in i.url:
                            users_footprint.append(i)

                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail



                elif select_box == '/forum/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if start_date <= created_obj:
                            obj_list.append(i)

                    for i in obj_list:
                        if i.url == '/forum/':
                            count_home_forum += 1

                        elif '/forum/category/' in i.url:
                            count_subcategory_forum += 1

                        elif '/forum/sub-category/topic/' in i.url:
                            count_subcategory_list_forum += 1

                        elif '/forum/topic/' in i.url:
                            count_topic_forum += 1


                        if '/forum/' in i.url:
                            users_footprint.append(i)
                    context['count_home_forum'] = count_home_forum
                    context['count_topic_forum'] = count_topic_forum
                    context['count_subcategory_forum'] = count_subcategory_forum
                    context['count_subcategory_list_forum'] = count_subcategory_list_forum


                elif select_box == '/projects/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if start_date <= created_obj:
                            obj_list.append(i)
                            
                    for i in obj_list:
                        if i.url == '/projects/':
                            count_obj += 1
                        elif 'project/detail/' in i.url:
                            count_detail += 1
                        if '/projects/' in i.url or '/project/detail/' in i.url:
                            users_footprint.append(i)
                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/dashboard/projects':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if start_date <= created_obj:
                            obj_list.append(i)
                            
                    for i in obj_list:
                        if i.url == '/dashboard/projects':
                            count_obj += 1
                        elif '/dashboard/project/detail/' in i.url:
                            count_detail += 1
                        if '/dashboard/projects' in i.url or '/dashboard/project/detail/' in i.url:
                            users_footprint.append(i)
                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/workshop/list-for-all/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if start_date <= created_obj:
                            obj_list.append(i)
                            
                    for i in obj_list:
                        if i.url == '/workshop/list-for-all/':
                            count_obj += 1
                        elif '/workshop/view-workshop/' in i.url:
                            count_detail += 1
                        if '/workshop/list-for-all/' in i.url or '/workshop/view-workshop/' in i.url:
                            users_footprint.append(i)
                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                else:
                    users_footprint = []
                    objs = UserFootprint.objects.filter(url=select_box).order_by('-created')
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if start_date <= created_obj:
                            users_footprint.append(i)


            elif end_date != '':
                if select_box == '/blog/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if end_date >= created_obj:
                            obj_list.append(i)

                    for i in obj_list:
                        if i.url == '/blog/':
                            count_obj += 1
                        elif '/blog/detail/' in i.url:
                            count_detail += 1
                        if '/blog/' in i.url:
                            users_footprint.append(i)

                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/news/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if end_date >= created_obj:
                            obj_list.append(i)

                    for i in obj_list:
                        if i.url == '/news/':
                            count_obj += 1
                        elif '/news_detail/' in i.url:
                            count_detail += 1
                        if '/news/' in i.url or '/news_detail/' in i.url:
                            users_footprint.append(i)

                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/videos/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if end_date >= created_obj:
                            obj_list.append(i)

                    for i in obj_list:
                        if i.url == '/videos/':
                            count_obj += 1
                        elif '/videos/detail/' in i.url:
                            count_detail += 1
                        if '/videos/' in i.url:
                            users_footprint.append(i)

                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/forum/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if end_date >= created_obj:
                            obj_list.append(i)

                    for i in obj_list:
                        if i.url == '/forum/':
                            count_home_forum += 1

                        elif '/forum/category/' in i.url:
                            count_subcategory_forum += 1

                        elif '/forum/sub-category/topic/' in i.url:
                            count_subcategory_list_forum += 1

                        elif '/forum/topic/' in i.url:
                            count_topic_forum += 1


                        if '/forum/' in i.url:
                            users_footprint.append(i)
                    context['count_home_forum'] = count_home_forum
                    context['count_topic_forum'] = count_topic_forum
                    context['count_subcategory_forum'] = count_subcategory_forum
                    context['count_subcategory_list_forum'] = count_subcategory_list_forum


                elif select_box == '/projects/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if end_date >= created_obj:
                            obj_list.append(i)
                            
                    for i in obj_list:
                        if i.url == '/projects/':
                            count_obj += 1
                        elif 'project/detail/' in i.url:
                            count_detail += 1
                        if '/projects/' in i.url or '/project/detail/' in i.url:
                            users_footprint.append(i)
                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/dashboard/projects':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if end_date >= created_obj:
                            obj_list.append(i)
                            
                    for i in obj_list:
                        if i.url == '/dashboard/projects':
                            count_obj += 1
                        elif '/dashboard/project/detail/' in i.url:
                            count_detail += 1
                        if '/dashboard/projects' in i.url or '/dashboard/project/detail/' in i.url:
                            users_footprint.append(i)
                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail

                elif select_box == '/workshop/list-for-all/':
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if end_date >= created_obj:
                            obj_list.append(i)
                            
                    for i in obj_list:
                        if i.url == '/workshop/list-for-all/':
                            count_obj += 1
                        elif '/workshop/view-workshop/' in i.url:
                            count_detail += 1
                        if '/workshop/list-for-all/' in i.url or '/workshop/view-workshop/' in i.url:
                            users_footprint.append(i)
                    context['count_obj'] = count_obj
                    context['count_detail'] = count_detail
                    

                else:
                    users_footprint = []
                    objs = UserFootprint.objects.filter(url=select_box).order_by('-created')
                    for i in objs:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if end_date >= created_obj:
                            users_footprint.append(i)


        elif position == 'project':
            obj_project = ResearchProject.objects.get(id=select_box)

            if start_date != '' and end_date != '':
                for i in objs:
                    created_obj = str(i.created)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]

                    if start_date <= created_obj and end_date >= created_obj :
                        if '/dashboard/project/detail/{}'.format(obj_project.id) == i.url or '/project/detail/{}'.format(obj_project.id) == i.url:
                            count_detail +=1
                            users_footprint.append(i)

                for i in applicants:
                    if i.project_request == obj_project:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if start_date <= created_obj and end_date >= created_obj:
                            all_applicant += 1

                        if i.status == 'request':
                            applay_applicant += 1

                        if i.status == 'accept':
                            accept_applicant += 1

                        if i.status == 'reject' or i.status == 'remove' or i.status == 'rejection-contract':
                            reject_applicant += 1

 
            elif start_date != '':
                for i in objs:
                    created_obj = str(i.created)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]

                    if '/dashboard/project/detail/{}'.format(obj_project.id) == i.url or '/project/detail/{}'.format(obj_project.id) == i.url and start_date <= created_obj:
                        count_detail +=1
                        users_footprint.append(i)



                for i in applicants:
                    if i.project_request == obj_project:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if start_date <= created_obj:
                            all_applicant += 1

                        if i.status == 'request':
                            applay_applicant += 1

                        if i.status == 'accept':
                            accept_applicant += 1

                        if i.status == 'reject' or i.status == 'remove' or i.status == 'rejection-contract':
                            reject_applicant += 1



            elif end_date != '':
                for i in objs:
                    created_obj = str(i.created)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]

                    if end_date >= created_obj :
                        if '/dashboard/project/detail/{}'.format(obj_project.id) == i.url or '/project/detail/{}'.format(obj_project.id) == i.url:
                            count_detail +=1
                            users_footprint.append(i)

                for i in applicants:
                    if i.project_request == obj_project:
                        created_obj = str(i.created)
                        created_obj = created_obj.split(' ')
                        created_obj = created_obj[0]

                        if end_date >= created_obj:
                            all_applicant += 1

                        if i.status == 'request':
                            applay_applicant += 1

                        if i.status == 'accept':
                            accept_applicant += 1

                        if i.status == 'reject' or i.status == 'remove' or i.status == 'rejection-contract':
                            reject_applicant += 1
                        
            context['obj_project'] = obj_project
            context['count_detail'] = count_detail
            context['all_applicant'] = all_applicant
            context['applay_applicant'] = applay_applicant
            context['accept_applicant'] = accept_applicant
            context['reject_applicant'] = reject_applicant



        elif position == 'register':
            if start_date != '' and end_date != '':
                for i in users:
                    created_obj = str(i.date_joined)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]

                    if start_date <= created_obj and end_date >= created_obj :
                        register_users.append(i)
                        
            elif end_date != '':
                for i in users:
                    created_obj = str(i.date_joined)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]

                    if end_date >= created_obj :
                        register_users.append(i)

            elif start_date != '':
                for i in users:
                    created_obj = str(i.date_joined)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]

                    if start_date <= created_obj :
                        register_users.append(i)

            context['register_users'] = register_users

        context['users_footprint'] = users_footprint

        return render(request, 'seo/user_footprint_ajax.html', context=context)
# 2022-07-25 <class 'str'>
# 2022-07-01 <class 'str'>

class LineChartJSONView(BaseLineChartView):
    def get_labels(self):
        """Return 7 labels for the x-axis."""
        global chart
        chart = []
        x_list = []
        if start_date != '' and end_date != '':
            start_date_int = start_date.split('-')
            end_date_int = end_date.split('-')
            start_date_d = date(int(start_date_int[0]), int(start_date_int[1]), int(start_date_int[2]))
            end_date_d = date(int(end_date_int[0]), int(end_date_int[1]), int(end_date_int[2]))

            start_date_d = start_date_d.strftime('%Y/%m/%d')
            end_date_d = end_date_d.strftime('%Y/%m/%d')
            
            start_date_d = time.mktime(datetime.datetime.strptime(start_date_d, '%Y/%m/%d').timetuple())
            end_date_d = time.mktime(datetime.datetime.strptime(end_date_d, '%Y/%m/%d').timetuple())

            count = 24*3600
            i = int(start_date_d)
            while i <= int(end_date_d):
                i += count
                x_list.append(i)

            for i in x_list:
                date_chart = datetime.datetime.fromtimestamp(i)
                date_chart = date_chart.strftime('%Y-%m-%d')
                chart.append(date_chart)
        return chart

    def get_providers(self):
        """Return names of datasets."""
        return ["Central", "Eastside", "Westside"]

    def get_data(self):
        """Return 3 datasets to plot."""
        obj_list = []
        objecs_list = []
        users = User.objects.all()
        if position == 'select_user':
            objecs_list = UserFootprint.objects.filter(user_id=select_box).order_by('-created')
        
        elif position == 'select_url':
            objs = UserFootprint.objects.all().order_by('-created')
            if select_box == '/blog/':
                for i in objs:
                    created_obj = str(i.created)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]

                    if start_date <= created_obj and end_date >= created_obj:
                        obj_list.append(i)

                for i in obj_list:
                    if '/blog/' in i.url:
                        objecs_list.append(i)

            elif select_box == '/news/':
                for i in objs:
                    created_obj = str(i.created)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]
                    if start_date <= created_obj and end_date >= created_obj:
                        obj_list.append(i)

                for i in obj_list:
                    if '/news/' in i.url or '/news_detail/' in i.url:
                        objecs_list.append(i)


            elif select_box == '/videos/':
                for i in objs:
                    created_obj = str(i.created)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]
                    if start_date <= created_obj and end_date >= created_obj:
                        obj_list.append(i)

                for i in obj_list:
                    if '/videos/' in i.url:
                        objecs_list.append(i)


            elif select_box == '/forum/':
                for i in objs:
                    created_obj = str(i.created)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]
                    if start_date <= created_obj and end_date >= created_obj:
                        obj_list.append(i)

                for i in obj_list:
                    if '/forum/' in i.url:
                        objecs_list.append(i)

            elif select_box == '/projects/':
                for i in objs:
                    created_obj = str(i.created)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]
                    if start_date <= created_obj and end_date >= created_obj:
                        obj_list.append(i)

                for i in obj_list:
                    if '/projects/' in i.url or '/project/detail/' in i.url:
                        objecs_list.append(i)

            elif select_box == '/dashboard/projects':
                for i in objs:
                    created_obj = str(i.created)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]
                    if start_date <= created_obj and end_date >= created_obj:
                        obj_list.append(i)

                for i in obj_list:
                    if '/dashboard/projects' in i.url or '/dashboard/project/detail/' in i.url:
                        objecs_list.append(i)

            elif select_box == '/workshop/list-for-all/':
                for i in objs:
                    created_obj = str(i.created)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]
                    if start_date <= created_obj and end_date >= created_obj:
                        obj_list.append(i)

                for i in obj_list:
                    if '/workshop/list-for-all/' in i.url or '/workshop/view-workshop/' in i.url:
                        objecs_list.append(i)
            else:
                objecs_list = []
                objs = UserFootprint.objects.filter(url=select_box).order_by('-created')
                for i in objs:
                    created_obj = str(i.created)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]

                    if start_date <= created_obj and end_date >= created_obj:
                        objecs_list.append(i)

        elif position == 'project':
            objs = UserFootprint.objects.all().order_by('-created')
            obj_project = ResearchProject.objects.get(id=select_box)

            if start_date != '' and end_date != '':
                for i in objs:
                    created_obj = str(i.created)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]

                    if start_date <= created_obj and end_date >= created_obj :
                        if '/dashboard/project/detail/{}'.format(obj_project.id) == i.url or '/project/detail/{}'.format(obj_project.id) == i.url:
                            objecs_list.append(i)
        
        elif position == 'register':
            if start_date != '' and end_date != '':
                for i in users:
                    created_obj = str(i.date_joined)
                    created_obj = created_obj.split(' ')
                    created_obj = created_obj[0]

                    if start_date <= created_obj and end_date >= created_obj :
                        objecs_list.append(i)


        x_chart = []
        count = 0
        # if position == 'select_user':

        for i in chart:
            for r in objecs_list:
                if position == 'register':
                    created_obj = str(r.date_joined)
                else:
                    created_obj = str(r.created)
                created_obj = created_obj.split(' ')
                created_obj = created_obj[0]
                if created_obj == i:
                    count += 1
            x_chart.append(count)
            count = 0







        return [x_chart,]




# class LineChartJSONView(BaseLineChartView):
#     def get_labels(self):
#         """Return 7 labels for the x-axis."""
#         if position == 'select_user':
#             return ["Home", "About us", "Guidelines", "News", "Videos", "Blog", "Forum", "FAQ", "Contact us", "Project home", "Project dashboard", "Workshop home"]
#         else:
#             return [1, 2,3 ,4 ,5]


#     def get_providers(self):
#         """Return names of datasets."""
#         return ["Central", "Eastside", "Westside"]

#     def get_data(self):
#         """Return 3 datasets to plot."""
#         objs = UserFootprint.objects.filter(user_id=select_box).order_by('-created')
#         user_chart = []
#         if position == 'select_user':
#             home_count = 0
#             aboutus_count = 0
#             guideline_count = 0
#             news_count = 0
#             videos_count = 0
#             blog_count = 0
#             forum_count = 0
#             FAQ_count = 0
#             contactus_count = 0
#             project_home_count = 0
#             project_dashboard_count = 0
#             workshop_home_count = 0
#             for i in objs:
#                 if i.url == '/':
#                     home_count += 1

#                 if i.url == '/about-us':
#                     aboutus_count += 1

#                 if i.url == '/guideline':
#                     guideline_count += 1

#                 if i.url == '/news/' or '/news_detail/' in i.url:
#                     news_count += 1

#                 if i.url == '/videos/' or '/videos/detail/' in i.url:
#                     videos_count += 1

#                 if i.url == '/blog/' or '/blog/detail/' in i.url:
#                     blog_count += 1

#                 if i.url == '/forum/' or '/forum/category/' in i.url or '/forum/topic/' in i.url or '/forum/sub-category/topic/' in i.url :
#                     forum_count += 1

#                 if i.url == '/FAQ/':
#                     FAQ_count += 1

#                 if i.url == '/contact-us/' :
#                     contactus_count += 1

#                 if i.url == '/projects/' or '/project/detail/' in i.url:
#                     project_home_count += 1

#                 if i.url == '/dashboard/projects' or '/dashboard/project/detail/' in i.url:
#                     project_dashboard_count += 1

#                 if i.url == '/workshop/list-for-all/' or '/workshop/view-workshop/' in i.url:
#                     workshop_home_count += 1
#             user_chart = [
#                 home_count, aboutus_count, guideline_count, news_count, 
#                 videos_count, blog_count, forum_count, FAQ_count, contactus_count, 
#                 project_home_count, project_dashboard_count, workshop_home_count, 
#             ]


#         if end_date != '' and start_date != '':
#             start_date_int = start_date.split('-')
#             end_date_int = end_date.split('-')
#             start_date_int = ('').join(start_date_int)
#             end_date_int = ('').join(end_date_int)
#             for i in range(int(start_date_int), int(end_date_int)+1):

#         return [user_chart,]




line_chart = TemplateView.as_view(template_name='line_chart.html')
line_chart_json = LineChartJSONView.as_view()