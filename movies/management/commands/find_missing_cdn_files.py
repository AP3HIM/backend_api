# movies/management/commands/find_missing_cdn_files.py

from django.core.management.base import BaseCommand
from movies.models import Movie

class Command(BaseCommand):
    help = "Find movies where the CDN URL might not correspond to actual R2 files"

    def handle(self, *args, **kwargs):
        CDN_DOMAIN = "https://cdn.papertigercinema.com"
        missing_thumbs = []
        missing_videos = []

        for movie in Movie.objects.all():
            if movie.thumbnail_url and movie.thumbnail_url.startswith(CDN_DOMAIN):
                filename = movie.thumbnail_url.split(CDN_DOMAIN + "/")[-1]
                # Simulate checking if it was uploaded
                # You'll replace this with actual R2 check later
                missing_thumbs.append(filename)

            if movie.video_url and movie.video_url.startswith(CDN_DOMAIN):
                filename = movie.video_url.split(CDN_DOMAIN + "/")[-1]
                missing_videos.append(filename)

        self.stdout.write(f"CDN Thumbnail references: {len(missing_thumbs)}")
        self.stdout.write(f"CDN Video references: {len(missing_videos)}")
        self.stdout.write("NOTE: These are not checked against actual R2 objects. Compare manually.")

        # Optionally print them all
        for path in missing_thumbs: self.stdout.write("THUMB: " + path)
        for path in missing_videos: self.stdout.write("VIDEO: " + path)
