# your_app_name/admin.py

from django.contrib import admin
from .models import Movie, Favorite
from django.template.defaultfilters import pluralize # Optional, for better messages

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'genre', 'is_featured', 'is_public_domain', 'is_hero')
    list_filter = ('is_public_domain', 'genre', 'is_featured', 'year', 'is_hero')
    search_fields = ('title', 'overview')
    actions = ['make_featured', 'remove_featured',  'make_hero', 'remove_hero', 'mark_public_domain', 'mark_not_public_domain'] # <--- ADD THESE

    def make_featured(self, request, queryset):
        """
        Admin action to set selected movies as featured.
        """
        updated_count = queryset.update(is_featured=True)
        self.message_user(
            request,
            f"{updated_count} movie{pluralize(updated_count)} successfully marked as featured."
        )
    make_featured.short_description = "Mark selected movies as featured"

    def remove_featured(self, request, queryset):
        """
        Admin action to remove selected movies from featured.
        """
        updated_count = queryset.update(is_featured=False)
        self.message_user(
            request,
            f"{updated_count} movie{pluralize(updated_count)} successfully removed from featured."
        )
    remove_featured.short_description = "Remove selected movies from featured"

    # --- NEW ACTIONS FOR PUBLIC DOMAIN ---
    def mark_public_domain(self, request, queryset):
        """
        Admin action to mark selected movies as public domain.
        """
        updated_count = queryset.update(is_public_domain=True)
        self.message_user(
            request,
            f"{updated_count} movie{pluralize(updated_count)} successfully marked as public domain."
        )
    mark_public_domain.short_description = "Mark selected movies as Public Domain"

    def mark_not_public_domain(self, request, queryset):
        """
        Admin action to mark selected movies as NOT public domain.
        """
        updated_count = queryset.update(is_public_domain=False)
        self.message_user(
            request,
            f"{updated_count} movie{pluralize(updated_count)} successfully marked as NOT Public Domain."
        )
    mark_not_public_domain.short_description = "Mark selected movies as NOT Public Domain"

    def make_hero(self, request, queryset):
        updated_count = queryset.update(is_hero=True)
        self.message_user(request, f"{updated_count} movie{pluralize(updated_count)} marked as Hero Carousel.")
    make_hero.short_description = "Mark selected movies for Hero Carousel"

    def remove_hero(self, request, queryset):
        updated_count = queryset.update(is_hero=False)
        self.message_user(request, f"{updated_count} movie{pluralize(updated_count)} removed from Hero Carousel.")
    remove_hero.short_description = "Remove selected movies from Hero Carousel"

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie')
    search_fields = ('user__username', 'movie__title')