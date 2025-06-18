# movies/management/commands/process_local_movies.py
"""
Bulk-processor for your local library.

Processes every Movie that either
  • has no thumbnail_url OR
  • video_url is not an .mp4

Per movie it will
  1. download to a temp dir
  2. convert ➜ .mp4 if needed   (ffmpeg)
  3. move final .mp4  → media/movies/<id>.mp4
  4. create thumbnail → media/movies/thumbnails/<id>.jpg
  5. update video_url + thumbnail_url in the DB
  6. remove the temp dir

Run examples
    python manage.py process_local_movies           # all pending
    python manage.py process_local_movies --limit 5 # only first 5
"""

import shutil
import tempfile
from pathlib import Path

import requests
from django.core.management.base import BaseCommand
from django.db.models import Q

from movies.models import Movie
from movies.utils import (
    ensure_dirs,
    MEDIA_MOVIE_PATH,
    THUMBNAIL_PATH,
    convert_to_mp4,
    generate_thumbnail,
)

# ---------- helpers -----------------------------------------------------------

def ascii_safe(text: str) -> str:
    """Return a console-safe ASCII version of *text* (ʔ → ?)."""
    return text.encode("ascii", "replace").decode("ascii")

CHUNK   = 1024 * 1024   # 1 MB
TIMEOUT = 30            # seconds


# ---------- command -----------------------------------------------------------

class Command(BaseCommand):
    help = "Download, convert, thumbnail and update Movie rows."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, default=None,
            help="Process at most N movies this run (testing / batching)."
        )

    # ------------------------------------------------------------------ #
    def handle(self, *args, **opts):
        ensure_dirs()

        qs = Movie.objects.filter(
            Q(thumbnail_url__isnull=True) |
            Q(thumbnail_url__exact="")    |
            ~Q(video_url__iendswith=".mp4")
        ).order_by("id")

        if opts["limit"]:
            qs = qs[: opts["limit"]]

        total = qs.count()
        if not total:
            self.stdout.write(self.style.SUCCESS("✔ No movies need processing."))
            return

        self.stdout.write(f"Processing {total} movie(s)...")

        for idx, movie in enumerate(qs, 1):
            self.stdout.write(
                f"\n[{idx}/{total}] {movie.id} - {ascii_safe(movie.title)}"
            )

            # ---- 0. skip obviously bad links ---------------------------------
            bad = (
                not movie.video_url or
                "watch?v=" in movie.video_url or
                movie.video_url.startswith(("https://youtu", "https://www.youtube"))
            )
            if bad:
                self.stderr.write("    skipped - video_url invalid")
                continue

            # ---- 1. download --------------------------------------------------
            tmp_dir  = Path(tempfile.mkdtemp())
            src_name = Path(movie.video_url).name
            src_path = tmp_dir / src_name
            try:
                with requests.get(movie.video_url, stream=True, timeout=TIMEOUT) as r:
                    r.raise_for_status()
                    with open(src_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=CHUNK):
                            if chunk:
                                f.write(chunk)
            except Exception as exc:
                self.stderr.write(f"    download failed: {exc}")
                shutil.rmtree(tmp_dir, ignore_errors=True)
                continue

            # ---- 2. convert if not mp4 ---------------------------------------
            if src_path.suffix.lower() != ".mp4":
                mp4_path = src_path.with_suffix(".mp4")
                if not convert_to_mp4(str(src_path), str(mp4_path)):
                    self.stderr.write("    conversion failed")
                    shutil.rmtree(tmp_dir, ignore_errors=True)
                    continue
                src_path = mp4_path

            # ---- 3. move final mp4 -------------------------------------------
            dest_name = f"{movie.id}.mp4"
            dest_path = Path(MEDIA_MOVIE_PATH) / dest_name
            shutil.move(src_path, dest_path)
            movie.video_url = f"/media/movies/{dest_name}"

            # ---- 4. thumbnail -------------------------------------------------
            thumb_name = f"{movie.id}.jpg"
            thumb_path = Path(THUMBNAIL_PATH) / thumb_name
            if generate_thumbnail(str(dest_path), str(thumb_path)):
                movie.thumbnail_url = f"/media/movies/thumbnails/{thumb_name}"
            else:
                self.stderr.write("    thumbnail generation failed")

            # ---- 5. save row --------------------------------------------------
            movie.save(update_fields=["video_url", "thumbnail_url"])
            self.stdout.write("    done")

            # ---- 6. cleanup ---------------------------------------------------
            shutil.rmtree(tmp_dir, ignore_errors=True)

        self.stdout.write(self.style.SUCCESS("All requested movies processed."))
