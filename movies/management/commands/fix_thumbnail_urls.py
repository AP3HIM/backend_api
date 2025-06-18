# movies/management/commands/fix_thumbnails_urls.py

from django.core.management.base import BaseCommand
from movies.models import Movie

class Command(BaseCommand):
    help = "Fix malformed CDN URLs in the database (e.g., duplicated paths or missing slashes)."

    def handle(self, *args, **kwargs):
        fixed_count = 0

        replacements = {
            # Duplicated segments
            "https://cdn.papertigercinema.com/media/movies/media/movies/": "https://cdn.papertigercinema.com/media/movies/",
            "https://cdn.papertigercinema.com/static/static/": "https://cdn.papertigercinema.com/static/",
            "https://cdn.papertigercinema.com/media/movies/thumbnails/media/movies/thumbnails/":
                "https://cdn.papertigercinema.com/media/movies/thumbnails/",

            # Just in case these appear too
            "https://cdn.papertigercinema.commedia/movies/": "https://cdn.papertigercinema.com/media/movies/",
            "https://cdn.papertigercinema.comstatic/static/": "https://cdn.papertigercinema.com/static/",
        }

        for movie in Movie.objects.all():
            original_video_url = movie.video_url or ""
            original_thumbnail_url = movie.thumbnail_url or ""
            movie_changed = False

            # Fix video_url
            for old, new in replacements.items():
                if old in movie.video_url:
                    new_url = movie.video_url.replace(old, new)
                    if new_url != movie.video_url:
                        self.stdout.write(f"✔ Fixed video URL for Movie {movie.id}:\n    {movie.video_url} →\n    {new_url}")
                        movie.video_url = new_url
                        movie_changed = True
                        break

            # Fix thumbnail_url
            for old, new in replacements.items():
                if old in movie.thumbnail_url:
                    new_url = movie.thumbnail_url.replace(old, new)
                    if new_url != movie.thumbnail_url:
                        self.stdout.write(f"✔ Fixed thumbnail URL for Movie {movie.id}:\n    {movie.thumbnail_url} →\n    {new_url}")
                        movie.thumbnail_url = new_url
                        movie_changed = True
                        break

            if movie_changed:
                movie.save()
                fixed_count += 1

        self.stdout.write(self.style.SUCCESS(f"\n✅ Updated {fixed_count} movie entries with corrected URLs."))
