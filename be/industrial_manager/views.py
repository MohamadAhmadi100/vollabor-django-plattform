from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.http import JsonResponse
from django.shortcuts import render

from industrial_manager.forms import IndustrialEmailForm
from industrial_manager.models import IndustrialManager
from industrial_manager.utils.industrial_email_utilities import *


@login_required
def industrial_email(request):
    if IndustrialManager.objects.filter(user=request.user).count() == 0:
        return render(request, 'ivc_website/403.html')

    email_form = IndustrialEmailForm()

    if request.method == "POST" :
        if 'get-data' in request.POST:
            success, length, last_modification_time = get_data_from_google_sheet(request.user.username)
            return JsonResponse({"success": success, 'length': length,
                                 'last_modification_time': naturaltime(last_modification_time)}, safe=True)
        if 'update-data' in request.POST:
            success, length, last_modification_time = update_data(request.user.username)
            return JsonResponse({"success": success, 'length': length,
                                 'last_modification_time': naturaltime(last_modification_time)}, safe=True)
        if 'get-country-list' in request.POST:
            success, result_list = get_country_list(request.user.username)
            return JsonResponse({"success": success, 'list': result_list}, safe=True)
        if 'get-all-list' in request.POST:
            success, length = get_all_list(request.user.username)
            return JsonResponse({"success": success, 'length': length}, safe=True)
        if 'get-a-country-number' in request.POST:
            country_name = request.POST['country-name']
            success, number = get_country_numbers(request.user.username, country_name)
            return JsonResponse({"success": success, 'number': number}, safe=True)
        if 'get-last-modification_time' in request.POST:
            success, last_modification_time = get_last_modification_time(request.user.username)
            return JsonResponse({"success": success, 'last_modification_time': naturaltime(last_modification_time)},
                                safe=True)
    context = {
        'email_form': email_form
    }
    return render(request, 'industrial_manager/industrial_email.html', context)
