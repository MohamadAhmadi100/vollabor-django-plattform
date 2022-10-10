from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from seo.forms import RobotsForm, TitleDescriptionForm
from seo.models import RobotsMeta, SEO, TitleAndDescription


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
