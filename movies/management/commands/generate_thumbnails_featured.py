# movies/management/commands/generate_thumbnails_featured.py

import os
import subprocess
from django.core.management.base import BaseCommand
from movies.models import Movie
from django.conf import settings

class Command(BaseCommand):
    help = "Generate thumbnails using FFmpeg for featured movies that are missing them."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Simulate actions without generating thumbnails.')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        featured_movies = Movie.objects.filter(is_featured=True)
        output_dir = os.path.join(settings.MEDIA_ROOT, 'movies', 'thumbnails')
        os.makedirs(output_dir, exist_ok=True)

        count = 0
        for movie in featured_movies:
            # Skip if there's already a real thumbnail
            if movie.thumbnail_url and movie.thumbnail_url.strip() != "" and "placeholder" not in movie.thumbnail_url:
                continue


            # Resolve video path
            video_path = movie.video_url.replace('/media/', os.path.join(str(settings.MEDIA_ROOT), ''))
            if not os.path.isfile(video_path):
                self.stdout.write(self.style.WARNING(f" X File not found: {video_path}"))
                continue

            # Prepare output path
            output_path = os.path.join(output_dir, f"{movie.id}_thumb.jpg")
            if not dry_run:
                command = [
                    "ffmpeg",
                    "-ss", "00:01:00",  # Jump to 1 minute mark
                    "-i", video_path,
                    "-frames:v", "1",
                    "-q:v", "2",
                    "-y",
                    output_path,
                ]
                try:
                    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    relative_url = os.path.relpath(output_path, settings.MEDIA_ROOT).replace("\\", "/")
                    movie.thumbnail_url = f"/media/{relative_url}"
                    movie.save()
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f"CHECK Thumbnail generated for {movie.title}"))
                except subprocess.CalledProcessError:
                    self.stdout.write(self.style.ERROR(f"X FFmpeg failed for {movie.title}"))
            else:
                self.stdout.write(f"Would generate thumbnail for: {movie.title}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {count if not dry_run else 'All'} thumbnails {'generated' if not dry_run else 'would be generated'}."
        ))
