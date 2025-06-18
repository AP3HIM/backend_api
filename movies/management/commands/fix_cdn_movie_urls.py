# movies/management/commands/fix_cdn_movie_urls.py

import os
from django.core.management.base import BaseCommand
from movies.models import Movie

CDN_DOMAIN = "https://cdn.papertigercinema.com"
BASE_MEDIA_PATH = "media/movies"
ARCHIVE_DOMAINS = ("https://archive.org", "http://archive.org")

class Command(BaseCommand):
    help = "Update movie URLs to CDN if local files exist and skip archive.org"

    def handle(self, *args, **kwargs):
        updated = 0
        skipped = 0
        missing = 0

        for movie in Movie.objects.all():
            changed = False

            # === VIDEO ===
            video_url = movie.video_url or ""
            if video_url.startswith(ARCHIVE_DOMAINS):
                skipped += 1
            elif video_url.startswith(CDN_DOMAIN):
                skipped += 1
            else:
                filename = os.path.basename(video_url)
                local_path = os.path.join(BASE_MEDIA_PATH, "videos", filename)
                if os.path.exists(local_path):
                    new_video_url = f"{CDN_DOMAIN}/movies/videos/{filename}"
                    if movie.video_url != new_video_url:
                        movie.video_url = new_video_url
                        changed = True
                else:
                    self.stdout.write(f"❌ Missing local video for Movie {movie.id}: {filename}")
                    missing += 1

            # === THUMBNAIL ===
            thumb_url = movie.thumbnail_url or ""
            if thumb_url.startswith(ARCHIVE_DOMAINS) or thumb_url.startswith(CDN_DOMAIN):
                skipped += 1
            else:
                filename = os.path.basename(thumb_url)
                local_path = os.path.join(BASE_MEDIA_PATH, "thumbnails", filename)
                if os.path.exists(local_path):
                    new_thumb_url = f"{CDN_DOMAIN}/movies/thumbnails/{filename}"
                    if movie.thumbnail_url != new_thumb_url:
                        movie.thumbnail_url = new_thumb_url
                        changed = True
                else:
                    self.stdout.write(f"❌ Missing local thumbnail for Movie {movie.id}: {filename}")
                    missing += 1

            if changed:
                movie.save()
                self.stdout.write(f"✅ Updated Movie {movie.id}")
                updated += 1
            else:
                skipped += 1

        self.stdout.write("\n🎬 Done updating movie CDN URLs.")
        self.stdout.write(f"✅ Updated: {updated}")
        self.stdout.write(f"⏭️ Skipped: {skipped}")
        self.stdout.write(f"❌ Missing local files: {missing}")
