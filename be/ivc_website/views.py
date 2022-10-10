from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils import translation
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from dashboard.project_request_handler import *
from users.models import TopSupervisor, MemberProfile, Role
from .forms import NewsForm, SendRepoertByMainSupervisor, SuggestionForm, VideoForm, VideoCategoryForm, CommentProjectForm
from .models import Visitor, Video, News, Document, NewsManager, NewsCategory, Event, Video, VideoCategory, SuggestionBox
import datetime
from django.views.generic import ListView, DetailView
from research.models import ResearchProject, SuperVizor, Mentor, Member, Lerner, CommentProject, ResearchRole
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from workshop.models import Workshop, TimeTable
from dashboard.models import Notification
from accounting.models import Membership
from django.utils import timezone
from datetime import timedelta
from seo.models import UserFootprint
from ivc_project.email_sender import send_new_email
from django.contrib.auth import logout

def translate_ir(request):
    if '.ir' in request.get_host():
        translation.activate('fa')
    return {}


def membership(request):
    context={
        
    }
    return render(request, 'ivc_website/Membership.html', context)


def check_visitor(request):
    today_date = datetime.date.today()
    address = request.META.get('HTTP_X_FORWARDED_FOR')
    if address:
        ip = address.split(",")[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')

    if Visitor.objects.filter(ip=ip, visit_date=today_date).count() == 0:
        new_visitor = Visitor(ip=ip, visit_date=today_date)
        new_visitor.save()
    return {'visitor_numbers': Visitor.objects.all().count()}


def my_custom_page_not_found_view(request, exception):
    """
    view to show 404 not found page
    """
    return render(request, 'ivc_website/404.html')


def my_custom_permission_denied_view(request, exception):
    """
    view to show permission denied page (403 error)
    """
    return render(request, 'ivc_website/403.html')


def my_custom_bad_request_view(request, exception):
    """
    view to show bad request page (400 error)
    """
    return render(request, 'ivc_website/400.html')


def my_custom_error_view(request):
    """
    view to show 500 server error
    """
    return render(request, 'ivc_website/500.html')


def home(request):
    if request.user.is_authenticated:
        create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)
    workshops = []
    for w in Workshop.objects.filter(status = 'Accept').all():
        times = TimeTable.objects.filter(workshop = w).last()
        if times.start_date > datetime.date.today():
            workshops.append( w )
    context = {
        'research_new': ResearchProject.objects.filter(status='new', view_project_home=True).order_by('-created'),
        'research_on_going': ResearchProject.objects.filter(status='on_going', view_project_home=True).order_by('-created'),
        'research_done': ResearchProject.objects.filter(status='done', view_project_home=True).order_by('-created'),
        'news': News.objects.filter(status = 'p', home = True),
        'events': Event.objects.filter(status = 'p', home = True),
        'workshop': workshops,
        # 'workshop': Workshop.objects.all(),
        'videos': list(Video.objects.filter(status = 'p', is_top=True))[:6],
        'testimonials': CommentProject.objects.filter(status="accepted")[:6],
    }

    if request.user.is_authenticated:
        supervisor_workshop = Role.objects.filter(user=request.user, position='supervisor').count()
        context['is_supervisor_workshop'] = supervisor_workshop
    return render(request, 'ivc_website/home.html', context)



def project_filter(request):
    projects = ResearchProject.objects.all()
    project_status = request.POST.getlist('project_status[]')
    project_grade = request.POST.getlist('project_grade[]')
    
    if project_status:
        projects = ResearchProject.objects.filter(status__in = project_status).order_by("-created")
    else:
        projects = ResearchProject.objects.filter(~Q(status="delete"),).order_by("-created")

    if project_grade:
        projects = ResearchProject.objects.filter(status_value__in = project_grade).order_by("-created")
  
    if project_status and project_grade:
        projects = ResearchProject.objects.filter(status__in = project_status, status_value__in = project_grade).order_by("-created")
    
    # Set up Pagination 
    
    context = {
        'object_list': projects,
         
    }
    return render(request, 'ivc_website/project_filter.html', context)



def project(request, **kwargs):
    if request.method == 'GET':
        #if request.user.is_authenticated:
         #   create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)
        #projects = ResearchProject.objects.filter(~Q(status__in=["delete", "under_process_supervisor"]),).order_by("-created")
    
        if request.user.is_authenticated:
            create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)
        # Set up Pagination 
        # p = Paginator(projects, 10)
        # page = request.GET.get('page')
        # project_pagination = p.get_page(page)
        projects = []
        projects_new = ResearchProject.objects.filter(status="new",).order_by("-created")
        projects_on_going = ResearchProject.objects.filter(status="on_going",).order_by("-created")
        projects_done = ResearchProject.objects.filter(status="done",).order_by("-created")
        
        for i in projects_new:
            projects.append(i)
        for i in projects_on_going:
            projects.append(i)
        for i in projects_done:
            projects.append(i)

        context = {
            'projects': projects,
            # 'project_pagination': project_pagination,
        }

        return render(request, 'ivc_website/projects.html', context)

    elif request.method == 'POST':
        text = request.POST.get('text')


        project_pagination = ResearchProject.objects.filter(project__client_form__formclint__title__icontains=text)

        context = {
            'project_pagination': project_pagination,
        }

        return render(request, 'ivc_website/projects.html', context)


    
class Projectlist(ListView):
    queryset = ResearchProject.objects.all().order_by("-created")
    template_name = 'ivc_website/projects.html'
    paginate_by = 10


# class DetailProject(DetailView):
#     template_name = 'ivc_website/projects-detail.html'
#     def get_object(self):
#         pk = self.kwargs.get('pk')
#         global detail_research_pr
#         detail_research_pr =  get_object_or_404(ResearchProject, pk=pk)
#         return detail_research_pr
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['supervisor'] = SuperVizor.objects.filter(research=detail_research_pr)
#         context['Mentor'] = Mentor.objects.filter(research=detail_research_pr)
#         context['Member'] = Member.objects.filter(research=detail_research_pr)
#         context['Lerner'] = Lerner.objects.filter(research=detail_research_pr)

#         supervisor_count = SuperVizor.objects.filter(research=detail_research_pr).count()
#         Mentor_count = Mentor.objects.filter(research=detail_research_pr).count()
#         Member_count = Member.objects.filter(research=detail_research_pr).count()
#         Lerner_count = Lerner.objects.filter(research=detail_research_pr).count()

#         memebrs_count = supervisor_count + Mentor_count+ Member_count+ Lerner_count
#         context['memebrs_count'] = memebrs_count
#         return context



def detail_project(request, pk):
    if request.user.is_authenticated:
        create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)
    template_name = 'ivc_website/projects-detail.html'
    detail_research_pr =  get_object_or_404(ResearchProject, pk=pk)

    if request.user.is_authenticated:
        create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)
    if request.method == 'POST':
        form = CommentProjectForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data.get('comment')
            email = form.cleaned_data.get('email')
            id_project = form.cleaned_data.get('id_project')
            
            comment = CommentProject.objects.create(comment=comment, email=email, user=request.user, status='new', commentproject_id=id_project)
            
            users = ResearchRole.objects.filter(comment_management=True)
            
            for i in users:
                Notification(title='Research (ID: {})'.format(detail_research_pr.project.client_form.formclint.id_project), 
                    description='A comment has been added to your list. Go to your dashboard and observe it.', target=i.user, 
                    link='research-comment-management').save()

            messages.success(request,'Your comment has been submitted successfully.')
            return redirect("projects-page-detail", detail_research_pr.pk)
    else:
        form = CommentProjectForm
    supervisor_count = SuperVizor.objects.filter(research=detail_research_pr).count()
    Mentor_count = Mentor.objects.filter(research=detail_research_pr).count()
    Member_count = Member.objects.filter(research=detail_research_pr).count()
    Lerner_count = Lerner.objects.filter(research=detail_research_pr).count()
    memebrs_count = supervisor_count + Mentor_count+ Member_count+ Lerner_count

    context = {
        'form': form,
        'comments': CommentProject.objects.filter(status='accepted', commentproject=detail_research_pr),
        'object': detail_research_pr,
        'supervisor' : SuperVizor.objects.filter(research=detail_research_pr),
        'Mentor' : Mentor.objects.filter(research=detail_research_pr),
        'Member' : Member.objects.filter(research=detail_research_pr),
        'Lerner' : Lerner.objects.filter(research=detail_research_pr),
        'memebrs_count' : memebrs_count
    }

    return render(request, template_name, context)




def videos_page(request):
    if request.user.is_authenticated:
        create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)
    videos = Video.objects.filter(status = 'p')
    top_video = [video for video in videos if video.is_top == True]
    category = VideoCategory.objects.filter(status = True)
    category_list = dict()
    i = 1
    for cat in category:
        category_list[i] = cat
        i += 1
    context = {
        'videos': videos,
        'top_video':top_video[:5],
        'category': category_list,
    }
    return render(request, 'ivc_website/videos.html', context)


def video_filter(request):
    videos = Video.objects.filter(status = 'p')
    category_list = request.POST.getlist('category_list[]')
    article_time = request.POST.get('date_time')
    search_word = request.POST.get('search_word')
    if search_word:
        videos = Video.objects.filter(status = 'p', title__contains = search_word)

    if category_list or article_time:
        selected_article = list(videos)
        if category_list:
            help_list = []
            for item in selected_article:
                #cat = item.category.active()
                cat = [category.title for category in item.category.active()]
                if any(item in cat for item in category_list):
                    pass
                else:
                    help_list.append(item)
            for i in help_list:
                    if i in selected_article:
                        selected_article.remove(i)

        if article_time:
            if article_time == "Last_week":
                start_time = timezone.now().date()
                new_time = start_time - timedelta(days=7)
                delta = start_time - new_time  # as timedelta
                days = [start_time - timedelta(days=i) for i in range(delta.days + 1)]
                help_list = []
                for item in selected_article:
                    if item.created not in days:
                        help_list.append(item)
                for i in help_list:
                    if i in selected_article:
                        selected_article.remove(i)

            if article_time == "Last_month":
                start_time = timezone.now().date()
                new_time = start_time - timedelta(days=30)
                delta = start_time - new_time  # as timedelta
                days = [start_time - timedelta(days=i) for i in range(delta.days + 1)]
                help_list = []
                for item in selected_article:
                    if item.created not in days:
                        help_list.append(item)
                for i in help_list:
                    if i in selected_article:
                        selected_article.remove(i)
        context = {
            'videos': set(selected_article),
        }
    else:
        context = {
            'videos': videos,
        }
    # return HttpResponse('whatttt')
    return render(request, 'ivc_website/video_filter.html', context)


def video_detail(request, pk):
    if request.user.is_authenticated:
        create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)
    video = Video.objects.get(pk = pk)
    video.seen += 1
    video.save()
    related_video = set()
    category = [category for category in video.category.active()]
    for cat in category:
        rel_video = cat.video.published()
        for item in rel_video:
            related_video.add(item)
    category = VideoCategory.objects.filter(status = True)
    context = {
        'video': video,
        "related_video": list(related_video)[:6],
        'category': category,
    }
    return render(request, 'ivc_website/video_detail.html', context)


def documents_page(request):
    archives = []
    for index, archive in enumerate(Document.objects.all()):
        if index % 3 == 0:
            archives.append([])  # append a new row
        archives[-1].append(archive)

    return render(request, 'ivc_website/documents.html', {'archive_documents': archives})


def goals_page(request):
    return render(request, 'ivc_website/goals.html')


def news(request):
    if request.user.is_authenticated:
        create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)
    news = News.objects.filter(status = "p")
    category_list = NewsCategory.objects.filter(status=True)
    top_news = []
    for item in news:
        if item.home == True:
            top_news.append(item)
    context = {
        "news":news,
        "last_news":list(news)[-1],
        "top_news":top_news[:3],
        "category_list":category_list,
    }
    return render(request, 'ivc_website/news.html',context)

def news_filter(request):
    news = News.objects.filter(status = "p")
    if request.POST.get('status') and request.POST.get('status')=='category':
        news=News.objects.filter(status="P",category__in=request.POST.getlist('catlist'))
    else:
    
        slug = request.POST.get('slug')
        search_word = request.POST.get('search_word')
        if search_word != "":
            news = News.objects.filter(status = "p", title__icontains = search_word)
        if slug != "":
            category = NewsCategory.objects.get(slug=slug, status=True)
            news = category.news.published()
    context = {
        "news":news,
    }
    return render(request, 'ivc_website/news_filter.html',context)


def news_detail(request, pk):
    if request.user.is_authenticated:
        create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)
    news = News.objects.get(pk=pk, status = "p")
    recent_news = News.objects.filter(status = "p").order_by('-date')
    related_news = set()
    category = [category for category in news.category.active()]
    for cat in category:
        rel_news = cat.news.published()
        for item in rel_news:
            related_news.add(item)
    context = {
        "news":news,
        "recent_news": recent_news[:5],
        "related_news": list(related_news)[:4],
    }
    return render(request, 'ivc_website/news_detail.html',context)

def news_category(request, slug):
    category = NewsCategory.objects.get(slug=slug, status=True)
    category_list = NewsCategory.objects.filter(status=True)
    context = {
        "category":category,
        "category_list":category_list,
    }
    return render(request, 'ivc_website/news_category.html',context)


def event(request):
    event = Event.objects.filter(status = "p")
    context = {
        "event":event,
    }
    return render(request, 'ivc_website/event.html',context)

def event_detail(request, pk):
    event = Event.objects.get(pk=pk, status = "p")
    context = {
        "event":event,
    }
    return render(request, 'ivc_website/event_detail.html',context)


def about_us(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)
        return render(request, "ivc_website/about_us.html")
        
        
def guideline(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)
        return render(request, "ivc_website/guideLine.html")


def suggestion_box(request):
    if request.method == "POST":
        return redirect('dashboard-page')
        new_form = SuggestionForm(request.POST)
        if new_form.is_valid():
            sugestion = new_form.save(commit=False)
            sugestion.save()
            messages.success(request, "Your suggestion send successfully")
            return redirect('home-page')
        else:
            messages.error(request, new_form.errors)
            return HttpResponseRedirect(request.path_info)


def video_manager(request):
    manager = NewsManager.objects.get(manager = request.user)
    if manager.is_super_author:
        videos = Video.objects.all()
    else:
        videos = Video.objects.filter(user = request.user)
    context = {
        'videos':videos,
        'author': manager,
    }

    return render(request, 'ivc_website/video_manager.html', context)


@login_required
def create_video(request):
    if request.method == "GET":
        author = NewsManager.objects.get(manager = request.user)
        video = VideoForm()
        context = {
            'video': video,
            'author': author,
        }
        return render(request, 'ivc_website/video_create_update.html', context)
    elif request.method == "POST":
        data = request.POST.copy()
        data['user'] = request.user
        video_form = VideoForm(data, request.FILES)
        if video_form.is_valid():
            video_form.save()
            messages.success(request, "video added successfully")
            return redirect(reverse('video-view'))
        else:
            messages.error(request, video_form.errors)
            return HttpResponseRedirect(request.path_info)

@login_required
def update_video(request, pk):
    video = Video.objects.get(pk=pk)
    author = NewsManager.objects.get(manager = request.user)
    if request.method == "GET":
        video_form = VideoForm(instance = video)
        context = {
            "video" : video_form,
            'author': author,
        }
        return render(request, "ivc_website/video_create_update.html", context)
    elif request.method == "POST":
        data = request.POST.copy()
        data['user'] = request.user
        video_form = VideoForm(data, request.FILES, instance=video)
        if video_form.is_valid():
            video_form.save()
            messages.success(request, "video updated successfully")
            return redirect('video-view')
        else:
            messages.error(request, video_form.errors)
            return HttpResponseRedirect(request.path_info)

def delete_video(request, pk):
    video = Video.objects.get(pk=pk)
    video.delete()
    messages.error(request, "video deleted successfully")
    return redirect('video-view')


@login_required
def create_video_category(request):
    if request.method == "GET":
        category = VideoCategoryForm()
        context = {
            'category': category,
        }
        return render(request, 'ivc_website/video_category_create_update.html', context)
    elif request.method == "POST":
        category = VideoCategoryForm(request.POST)
        if category.is_valid():
            category.save()
            messages.success(request, 'Category created successfully')
            return redirect(reverse('video-view'))
        else:
            messages.error(request, category.errors)
            return redirect(reverse('video-view'))
            
            
def membership_front(request):
    template_name="ivc_website/Membership.html"

    context={
        'memberships':Membership.objects.all()
    }
    return render(request,template_name,context)


def messages_box(request):
    template_name='ivc_website/messages.html'
    smessages=SuggestionBox.objects.all().order_by('-created')
    
    if request.method == "POST":
        if request.POST.get('action') == 'is_read':
            message_id=request.POST.get('message_id')
            message=SuggestionBox.objects.get(pk=message_id)
            message.is_read=True
            message.save()
    
        else:
            email=request.POST.get('email')
            replymessage=request.POST.get('replymessage')
            message_id=request.POST.get('id')
            message=get_object_or_404(SuggestionBox,pk=message_id)
            message.is_reply=True
            message.reply_date=datetime.datetime.now()
            message.reply_message=replymessage
            message.save()
            send_new_email('', replymessage, email)
            messages.success(request,'Your reply sent')
            return redirect('messages')
    
    
    
    
    context={
    'suggests':smessages
    }
    
    return render(request,template_name,context)
    
def contact_us(request):
    template_name='ivc_website/contact_us.html'
    departments=[
    'Site section',
    'Project section',
    'Advertisement section',
    'Administrative section',
    'Workshop section',
    'Administratorship',
    ]
    
    if request.method == "POST":
        department=request.POST.get('department')
        email=request.POST.get('email')
        description=request.POST.get('description')
        SuggestionBox.objects.create(department=department.split(' ')[0],email=email,description=description)
        messages.success(request,'Your message has been sent.')
        return redirect('contact-us')
    
    context = {
    'departments':departments
    }
    return render(request,template_name,context)
    
    
def LogoutView(request):
    logout(request)
    return redirect('/')
