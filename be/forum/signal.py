from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# @receiver(post_save, sender=ResearchProject)
# def new_project_research(sender, instance, created, **kwargs):