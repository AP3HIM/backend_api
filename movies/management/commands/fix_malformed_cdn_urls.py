from django.core.management.base import BaseCommand
from movies.models import Movie

class Command(BaseCommand):
    help = "Fix malformed URLs where CDN was prepended to archive.org links"

    def handle(self, *args, **kwargs):
        fixed = 0
        bad_prefix = "https://cdn.papertigercinema.comhttps://"

        for movie in Movie.objects.all():
            changed = False

            # DEBUG: print first 5 URLs to check format
            if movie.id <= 890:  # limit output a bit
                self.stdout.write(f"Movie {movie.id} video_url: {movie.video_url}")
                self.stdout.write(f"Movie {movie.id} thumbnail_url: {movie.thumbnail_url}")

            # Fix video_url
            if movie.video_url and bad_prefix in movie.video_url:
                old_url = movie.video_url
                # Replace *only* the bad prefix once
                movie.video_url = movie.video_url.replace(bad_prefix, "https://", 1)
                self.stdout.write(f"✅ Fixed video URL for Movie {movie.id}: {old_url} → {movie.video_url}")
                changed = True

            # Fix thumbnail_url
            if movie.thumbnail_url and bad_prefix in movie.thumbnail_url:
                old_url = movie.thumbnail_url
                movie.thumbnail_url = movie.thumbnail_url.replace(bad_prefix, "https://", 1)
                self.stdout.write(f"✅ Fixed thumbnail URL for Movie {movie.id}: {old_url} → {movie.thumbnail_url}")
                changed = True

            if changed:
                movie.save()
                fixed += 1

        self.stdout.write(self.style.SUCCESS(f"🔧 Fixed {fixed} malformed URLs"))
