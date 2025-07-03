from django.contrib.sitemaps import Sitemap
from .models import Movie
from django.urls import reverse

class MovieSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return Movie.objects.all()

    def location(self, obj):
        return f"/movies/{obj.slug}"

class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return ['home', 'about', 'terms', 'privacy', 'copyright']

    def location(self, item):
        return reverse(item)

class GenreSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return [
            'Horror', 'Western', 'Thriller', 'Action', 'Romance',
            'Comedy', 'Drama', 'Sci-Fi'
        ]

    def location(self, genre):
        return f"/genre/{genre}"
