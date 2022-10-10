from datetime import datetime

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Article
from .models import Project


class StaticViewSitemap(Sitemap):
    
    changefreq = "daily"
    
    def items(self):
        return ['home-page','list-for-all', 'projects-page', 'FAQ-page', 'blog:blog-page', 'guideline', 'about-us', 'news-page']

    def location(self, item):
        return reverse(item)

    def lastmod(self, obj):
        if obj == 'home-page':
            return datetime.now()
        else:
            return datetime(2021, 7, 9)

    def priority(self, item):
        return {'home-page': 1.0, 'list-for-all': 0.9, 'projects-page': 0.9, 'FAQ-page': 0.9, 'blog:blog-page': 0.75, 'guideline':0.7, 'about-us':0.8, 'news-page':0.75, }[item]



class BlogSitemap(Sitemap):
    
    changefreq = "monthly"
    priority = 0.45
    
    def items(self):
        return Article.objects.all()

    def location(self, item):
        return reverse('blog:blog-detail', args=[item.pk])

    def lastmod(self, obj):
        return obj.created
