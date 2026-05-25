from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.services.models import Service


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8
    protocol = "https"

    def items(self):
        return ["core:home", "core:about", "core:contact", "services:list", "quotes:request"]

    def location(self, item):
        return reverse(item)


class HomePageSitemap(StaticViewSitemap):
    priority = 1.0
    changefreq = "weekly"

    def items(self):
        return ["core:home"]


class ServiceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7
    protocol = "https"

    def items(self):
        return Service.objects.filter(is_active=True)

    def location(self, obj):
        return obj.get_absolute_url()
