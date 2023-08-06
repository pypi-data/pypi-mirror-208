from django.contrib import sitemaps
from humans.models import Human

class HumansSitemap(sitemaps.Sitemap):
    protocol = "https"
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return Human.objects.filter(isPublished=True)
