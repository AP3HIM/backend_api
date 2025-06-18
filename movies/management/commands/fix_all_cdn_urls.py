# movies/management/commands/fix_all_cdn_urls.py

from django.core.management.base import BaseCommand
from movies.models import Movie

CDN_BASE = "https://cdn.papertigercinema.com"

class Command(BaseCommand):
    help = "Fix malformed relative and duplicated CDN URLs in movie records."

    def handle(self, *args, **kwargs):
        fixed = 0

        for movie in Movie.objects.all():
            changed = False

            original_video = movie.video_url or ""
            original_thumb = movie.thumbnail_url or ""

            new_video = self.clean_path(original_video, is_video=True)
            new_thumb = self.clean_path(original_thumb, is_video=False)

            if new_video != original_video:
                self.stdout.write(f"🎬 Video URL for Movie {movie.id}:\n  {original_video}\n→ {new_video}")
                movie.video_url = new_video
                changed = True

            if new_thumb != original_thumb:
                self.stdout.write(f"🖼️  Thumbnail URL for Movie {movie.id}:\n  {original_thumb}\n→ {new_thumb}")
                movie.thumbnail_url = new_thumb
                changed = True

            if changed:
                movie.save()
                fixed += 1

        self.stdout.write(self.style.SUCCESS(f"\n✅ Fixed {fixed} malformed movie URLs."))

    def clean_path(self, url, is_video):
        if url.startswith("https://archive.org/"):
            return url  # leave archive URLs untouched

        # Fix doubled media/static paths
        url = url.replace("media/movies/media/movies/", "media/movies/")
        url = url.replace("static/static/", "static/")
        url = url.replace("media/movies/thumbnails/media/movies/thumbnails/", "media/movies/thumbnails/")

        # Normalize relative to full CDN paths
        if url.startswith("media/movies/"):
            return f"{CDN_BASE}/media/movies/{url[len('media/movies/'):]}"
        if url.startswith("media/movies/thumbnails/"):
            return f"{CDN_BASE}/media/movies/thumbnails/{url[len('media/movies/thumbnails/'):]}"
        if url.startswith("static/"):
            return f"{CDN_BASE}/static/{url[len('static/'):]}"
        return url
