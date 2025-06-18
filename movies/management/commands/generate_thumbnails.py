from django.core.management.base import BaseCommand
from movies.models import Movie
import os
import subprocess
from django.conf import settings

class Command(BaseCommand):
    help = "Generate thumbnails for movies"

    def handle(self, *args, **kwargs):
        video_dir = os.path.join(settings.MEDIA_ROOT, "movies")
        thumb_dir = os.path.join(settings.MEDIA_ROOT, "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)

        for movie in Movie.objects.all():
            if movie.thumbnail_url:
                continue  # Skip if already has thumbnail

            filename = os.path.basename(movie.video_url)
            video_path = os.path.join(video_dir, filename)
            if not os.path.exists(video_path):
                self.stdout.write(self.style.WARNING(f"Video not found: {video_path}"))
                continue

            thumbnail_name = filename.rsplit('.', 1)[0] + ".jpg"
            thumbnail_path = os.path.join(thumb_dir, thumbnail_name)

            self.stdout.write(f"Generating thumbnail for: {movie.title}")
            subprocess.run([
                "ffmpeg", "-i", video_path,
                "-ss", "00:00:10", "-vframes", "1",
                thumbnail_path
            ])

            # Update movie.thumbnail_url (e.g., /media/thumbnails/movie.jpg)
            movie.thumbnail_url = f"/media/thumbnails/{thumbnail_name}"
            movie.save()
