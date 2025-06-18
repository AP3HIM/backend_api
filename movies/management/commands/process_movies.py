import os
import subprocess
from django.core.management.base import BaseCommand
from movies.models import Movie
from django.conf import settings

MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'media', 'movies')
THUMBNAIL_DIR = os.path.join(settings.BASE_DIR, 'media', 'thumbnails')

class Command(BaseCommand):
    help = 'Convert .avi to .mp4 and extract thumbnails using ffmpeg'

    def handle(self, *args, **kwargs):
        os.makedirs(MEDIA_ROOT, exist_ok=True)
        os.makedirs(THUMBNAIL_DIR, exist_ok=True)

        for movie in Movie.objects.all():
            if not movie.archive_identifier:
                continue

            avi_path = os.path.join(MEDIA_ROOT, f"{movie.archive_identifier}.avi")
            mp4_path = os.path.join(MEDIA_ROOT, f"{movie.archive_identifier}.mp4")
            thumbnail_path = os.path.join(THUMBNAIL_DIR, f"{movie.archive_identifier}.jpg")

            # Skip if already processed
            if os.path.exists(mp4_path) and os.path.exists(thumbnail_path):
                self.stdout.write(f"✔ Skipping {movie.title}, already processed")
                continue

            # Convert .avi to .mp4
            if os.path.exists(avi_path):
                self.stdout.write(f"▶ Converting {movie.title}...")
                subprocess.run([
                    "ffmpeg", "-y", "-i", avi_path, "-c:v", "libx264", "-preset", "fast",
                    "-crf", "23", "-c:a", "aac", mp4_path
                ])

                # Extract thumbnail
                self.stdout.write(f"🖼 Extracting thumbnail for {movie.title}...")
                subprocess.run([
                    "ffmpeg", "-y", "-i", mp4_path, "-ss", "00:00:05", "-vframes", "1", thumbnail_path
                ])

                # Update model and save
                movie.video_url = f"/media/movies/{os.path.basename(mp4_path)}"
                movie.thumbnail_url = f"/media/thumbnails/{os.path.basename(thumbnail_path)}"
                movie.save()

                # Delete original .avi
                os.remove(avi_path)
                self.stdout.write(f"🗑 Deleted original .avi for {movie.title}")

            else:
                self.stdout.write(f"⚠ AVI not found for {movie.title}")
