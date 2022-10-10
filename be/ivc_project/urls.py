"""ivc_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django import urls
from django.contrib import admin
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from ivc_website.models import News
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from ivc_website.views import LogoutView
from users.views import CustomLoginView, CustomPasswordResetView, login_view

from ivc_website.sitemaps import StaticViewSitemap, BlogSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogSitemap
}

urlpatterns = [
    path('workshop/',include('workshop.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path('lordoftherings/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('cartable/', include('cartable.urls')),
    path('coin/', include('coin.urls')),
    # add the robots.txt file
    path("robots.txt", TemplateView.as_view(template_name="ivc_website/robots.txt", content_type="text/plain")),
    path('blog/', include('blog.urls')),
    path('comment/', include('comment.urls')),
    path('forum/', include('forum.urls')),
    path('something/paypal/', include('paypal.standard.ipn.urls')),
    path('emails/', include('email_app.urls')),
    path('research/', include('research.urls')),
    path('zarinpal/', include('zarinpal.urls')),
    path('accounting/', include('accounting.urls')),

]

urlpatterns += i18n_patterns(
    path('', include('ivc_website.urls')),

    path('members/', include('users.urls')),
    path('archives/courses/', include('courses.urls')),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView, name='logout'),
    path('password-reset/', CustomPasswordResetView.as_view(template_name='users/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
    path('cv/', include('join.urls')),
    path('admin/clearcache/', include('clearcache.urls')),
    path('seo/', include('seo.urls')),
    path('industrial-manager/', include('industrial_manager.urls')),
    path('create-competition/', include('competition.urls')),
    # path('collaborate/', include('collaborate_with_us.urls')),
    path('FAQ/', include('FAQ.urls')),
    path('Q-AND-A/', include('Q_And_A.urls')),
    path('international-payment/', include('payment_stripe.urls')),
    path('workshop/', include('workshop.urls')),
    path('task_tracker/', include('task_tracker.urls')),
    path('request/', include('request.urls')),
    
    prefix_default_language=False
)

handler404 = 'ivc_website.views.my_custom_page_not_found_view'
handler403 = 'ivc_website.views.my_custom_permission_denied_view'
handler400 = 'ivc_website.views.my_custom_bad_request_view'
handler500 = 'ivc_website.views.my_custom_error_view'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
