from django.core.management.base import BaseCommand
from movies.models import Movie
import os
import subprocess
from django.conf import settings

class Command(BaseCommand):
    help = "Convert all .avi movie files to .mp4"

    def handle(self, *args, **kwargs):
        video_dir = os.path.join(settings.MEDIA_ROOT, "movies")

        for movie in Movie.objects.all():
            url = movie.video_url
            if not url.endswith(".avi"):
                continue

            filename = os.path.basename(url)
            input_path = os.path.join(video_dir, filename)

            if not os.path.exists(input_path):
                self.stdout.write(self.style.WARNING(f"File not found: {input_path}"))
                continue

            output_path = input_path.replace(".avi", ".mp4")

            self.stdout.write(f"Converting: {input_path}")
            subprocess.run([
                "ffmpeg", "-i", input_path,
                "-c:v", "libx264",
                "-c:a", "aac",
                output_path
            ])

            # Optional: update movie.video_url if you want
            new_url = url.replace(".avi", ".mp4")
            movie.video_url = new_url
            movie.save()
