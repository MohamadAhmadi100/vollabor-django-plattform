from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import messages
from .models import Letter, Receiver, Staff, section_choices, Refer
from django.utils import timezone
from django.contrib.auth.models import User


def cartable_panel(request):
    my_letter_send = Letter.objects.filter(sender=request.user)
    my_receiver = Receiver.objects.filter(receiver=request.user)
    my_letter = Letter.objects.all()
    total_receiver = Receiver.objects.all()
    new_refer = Refer.objects.filter(receiver=request.user)

    content = {
        'letters': my_letter,
        'receivers': my_receiver,
        'sends': my_letter_send,
        'receiver': total_receiver,
        'refers': new_refer,
    }

    return render(request, 'cartable/cartable.html', content)


def send_new_letter_panel(request):
    # number = ''
    # time = timezone.localtime()
    # time_to_str = "{},{},{},{},{}".format(time.year, time.month, time.day, time.hour, time.minute)
    # for i in time_to_str:
    #     if i != ',':
    #         number += i

    if request.method == 'POST':
        print(request.POST)

        new_letter = Letter(sender=request.user)
        if request.POST.get('title') is None or request.POST.get('title').strip() == "":
            messages.error(request, "error: title is empty")
            return HttpResponseRedirect(request.path_info)
        else:
            new_letter.title = request.POST.get('title')

        if request.POST.get('summary') is None or request.POST.get('summary').strip() == "":
            messages.error(request, "error: summary is empty")
            return HttpResponseRedirect(request.path_info)
        else:
            new_letter.summary = request.POST.get('summary')

        if request.POST.get('letter-security') is None or request.POST.get('letter-security').strip() == "":
            messages.error(request, "error: security is empty")
            return HttpResponseRedirect(request.path_info)
        else:
            new_letter.security = request.POST.get('letter-security')

        if request.POST.get('letter-priority') is None or request.POST.get('letter-priority').strip() == "":
            messages.error(request, "error : priority is empty")
            return HttpResponseRedirect(request.path_info)
        else:
            new_letter.priority = request.POST.get('letter-priority')

       # if request.POST.get('document') is None or request.POST.get('document').strip() == "":
        #    messages.error(request, "error : document is empty")
         #   return HttpResponseRedirect(request.path_info)
        #else:
         #   new_letter.document = request.POST.get('document')
            
            
        if request.FILES['document'] is None:
            messages.error(request, "error : document is empty")
            return HttpResponseRedirect(request.path_info)
        else:
            new_letter.document = request.FILES['document']
            
            
        
        new_letter.attach_file = request.FILES['attachment']
       
        
        
        

        new_letter.save()
        new_letter.number = new_letter.id
        new_letter.save()

        if request.POST.get('orginal') is None or request.POST.get('orginal').strip() == "":
            messages.error(request, "error : orginal is empty")
            return HttpResponseRedirect(request.path_info)
        else:
            receivers = request.POST.getlist('orginal')
        print(receivers)
        users = User.objects.all()

        for rec in receivers:
            for user in users:
                if user.username == rec:
                    print('okkkkkk')

                    new_receiver = Receiver(receiver=user)
                    new_receiver.letter = new_letter
                    new_receiver.save()

        messages.success(request, "The letter has been send successfully")
        return HttpResponseRedirect(request.path_info)

    #############################################################################################################################

    my_staffs = Staff.objects.all()
    # sections = Staff.objects.values('section').distinct()
    section_lists = [s[0] for s in section_choices]
    context = {
        'staffs': my_staffs,
        'section_list': section_lists,
    }
    return render(request, 'cartable/send-new-letter.html', context)


def cartable_letter(request):
    if request.method == 'POST':
        print(request.POST)

        if 'cm' in request.POST:
            pk = request.POST.get('let')
            print(pk)
            new_letter = Letter.objects.get(pk=pk)

            new_refer = Refer(refer=request.user, sender=new_letter.sender, letter=new_letter)
            if request.POST.get('cm') is None or request.POST.get('cm').strip() == "":
                messages.error(request, "error : cm is empty")
                return HttpResponseRedirect(request.path_info)
            else:
                new_refer.text = request.POST.get('cm')
            new_refer.document = request.POST.get('document')

            if request.POST.get('receiver') is None or request.POST.get('receiver').strip() == "":
                messages.error(request, "error : receiver is empty")
                return HttpResponseRedirect(request.path_info)
            else:
                receivers = request.POST.getlist('receiver')
                
            if request.FILES['document'] is None:
                messages.error(request, "error : document is empty")
                return HttpResponseRedirect(request.path_info)
            else:
                new_refer.document = request.FILES['document']
                
           
            users = User.objects.all()

            for rec in receivers:
                for user in users:
                    if user.username == rec:
                        new_refer.receiver = user
                        new_refer.save()

            return HttpResponse("The refer has been send successfully")

        else:

            pk = request.POST.get('let.id')
            print(pk)
            new_letter = Letter.objects.get(pk=pk)

            receivers = Receiver.objects.filter(letter=new_letter)
            staffs = Staff.objects.all()

            section = []
            for rec in receivers:
                for staff in staffs:
                    if rec.receiver == staff.user:
                        if staff.section in section:
                            pass
                        else:
                            section.append(staff.section)

            content = {
                'letters': new_letter,
                'receivers': receivers,
                'staffs': staffs,
                'sections': section,

            }

            return render(request, 'cartable/cartable-letter.html', content)


def refer_letter(request, pk):
    new_refer = Refer.objects.get(pk=pk)

    letters = Letter.objects.all()

    staffs = Staff.objects.all()

    section = []

    # for staff in staffs:
    #     if staff.user == new_refer.sender:
    #
    #         if staff.section in section:
    #             pass
    #         else:
    #             section.append(staff.section)

    content = {
        'refer': new_refer,
        'letters': letters,
        'sections': section,
        'staffs': staffs,

    }

    return render(request, 'cartable/refer-letter.html', content)


def send_letter(request, pk):
    new_letter = Letter.objects.get(pk=pk)
    receivers = Receiver.objects.filter(letter=new_letter)
    staffs = Staff.objects.all()

    section = []
    for rec in receivers:
        for staff in staffs:
            if rec.receiver == staff.user:
                if staff.section in section:
                    pass
                else:
                    section.append(staff.section)

    content = {
        'letters': new_letter,
        'receivers': receivers,
        'staffs': staffs,
        'sections': section,

    }

    return render(request, "cartable/sent-letter.html", content)
    

    
