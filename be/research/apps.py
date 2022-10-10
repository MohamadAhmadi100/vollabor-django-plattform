from django.apps import AppConfig


class ResearchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'research'
    

    verbose_name = 'Project'
    verbose_name_plural = 'Projects'



    def ready(self):
        import research.notifications
