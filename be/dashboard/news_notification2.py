from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse

from courses.models import Course
from ivc_website.models import Project, NewsManager
from users.models import MemberProfile
from .models import Notification


@receiver(post_save, sender=Course)
@receiver(post_save, sender=MemberProfile)
@receiver(post_save, sender=Project)
def add_notification_for_news_managers(sender, instance, created, **kwargs):
    news_managers = NewsManager.objects.all()
    if sender == Course:
        if created:
            for news_manager in news_managers:
                Notification(title='NEWS ALERT!', description=f'New course has been added: {instance}',
                             target=news_manager.manager, link=reverse('courses-page')).save()
    if sender == MemberProfile:
        if created:
            for news_manager in news_managers:
                Notification(title='NEWS ALERT!', description=f'New member has been added: {instance}',
                             target=news_manager.manager,
                             link=reverse('dashboard-profile-page', args=[instance.id])).save()
    if sender == Project:
        if not created:
            if instance.is_valid:
                for news_manager in news_managers:
                    Notification(title='NEWS ALERT!', description=f'There has been a change in a project: {instance}',
                                 target=news_manager.manager, link=reverse('dashboard-project-view-page', args=[instance.pk])).save()
