# movies/management/commands/update_movie_urls.py

import os
from django.core.management.base import BaseCommand
from movies.models import Movie

CDN_DOMAIN = "https://cdn.papertigercinema.com"
LOCAL_VIDEO_DIR = "media/movies"
LOCAL_THUMB_DIR = "media/movies/thumbnails"

class Command(BaseCommand):
    help = "Update movie URLs to CDN if the local file exists"

    def handle(self, *args, **kwargs):
        updated = 0
        skipped = 0
        missing = 0

        for movie in Movie.objects.all():
            changed = False

            # === Thumbnail ===
            thumb = movie.thumbnail_url or ""
            if "movies/thumbnails/" in thumb:
                thumb_filename = thumb.split("movies/thumbnails/")[-1]
                local_thumb_path = os.path.join(LOCAL_THUMB_DIR, thumb_filename)
                if os.path.exists(local_thumb_path):
                    new_thumb_url = f"{CDN_DOMAIN}/movies/thumbnails/{thumb_filename}"
                    if movie.thumbnail_url != new_thumb_url:
                        movie.thumbnail_url = new_thumb_url
                        changed = True
                else:
                    self.stdout.write(f"[MISSING THUMBNAIL] {movie.id} - {thumb_filename}")
                    missing += 1

            # === Video ===
            video = movie.video_url or ""
            if "movies/videos/" in video:
                video_filename = video.split("movies/videos/")[-1]
                local_video_path = os.path.join(LOCAL_VIDEO_DIR, video_filename)
                if os.path.exists(local_video_path):
                    new_video_url = f"{CDN_DOMAIN}/movies/videos/{video_filename}"
                    if movie.video_url != new_video_url:
                        movie.video_url = new_video_url
                        changed = True
                else:
                    self.stdout.write(f"[MISSING VIDEO] {movie.id} - {video_filename}")
                    missing += 1

            if changed:
                movie.save()
                updated += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(" CDN URL Fix Summary"))
        self.stdout.write(f"    Updated URLs: {updated}")
        self.stdout.write(f"    Skipped (already correct or remote): {skipped}")
        self.stdout.write(f"    Missing local files: {missing}")
