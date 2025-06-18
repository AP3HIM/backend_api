import io
import logging
from pathlib import Path
from hashlib import md5

import requests
from PIL import Image

from django.conf import settings
from django.core.management.base import BaseCommand
from movies.models             import Movie

log = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# Tweaks you may want to change
# ----------------------------------------------------------------------
# Where the good placeholder lives (served by Django static files)
PLACEHOLDER_REL  = "placerholder_thumbnail.jpg"
PLACEHOLDER_URL  = settings.STATIC_URL.rstrip("/") + f"/{PLACEHOLDER_REL}"

# Local thumbs you created earlier – used when thumbnail_url is a bare filename
THUMB_DIR        = Path(settings.MEDIA_ROOT) / "movies" / "thumbnails"

# “Mostly-black” detector heuristics
BLACK_THRESHOLD  = 15      # 0-255; values below are considered “black”
BLACK_PERCENTAGE = 0.96    # ≥ 96 % black pixels  ⇒  bad thumbnail
# ----------------------------------------------------------------------


def _hash(img: Image.Image) -> str:
    """Cheap image hash to recognise archive.org’s repeated frames."""
    with io.BytesIO() as buf:
        img.resize((64, 64)).convert("L").save(buf, "PNG")
        return md5(buf.getvalue()).hexdigest()


# Add any known-bad hashes here (after you see them printed once)
KNOWN_BAD_HASHES: set[str] = {
    # "b04dcaf1774d84ca7e5cdec3d9a4711f",  # ← example
}


def is_mostly_black(img: Image.Image) -> bool:
    """True if ≥ BLACK_PERCENTAGE of pixels are below BLACK_THRESHOLD."""
    gray   = img.convert("L")
    hist   = gray.histogram()
    dark   = sum(hist[:BLACK_THRESHOLD])
    return (dark / sum(hist)) >= BLACK_PERCENTAGE


def load_image(url_or_path: str) -> Image.Image | None:
    """
    Try to open a thumbnail given either an http(s) url or a local relative path.
    Returns PIL Image or None on any failure.
    """
    try:
        if url_or_path.startswith("http"):
            resp = requests.get(url_or_path, timeout=10)
            resp.raise_for_status()
            return Image.open(io.BytesIO(resp.content))
        else:  # local
            p = Path(url_or_path)
            if not p.is_absolute():
                p = THUMB_DIR / p.name
            return Image.open(p)
    except Exception as exc:
        log.debug("Could not open %s: %s", url_or_path, exc)
        return None


class Command(BaseCommand):
    help = "Replace useless thumbnails (black, repeated, missing) with a colourful placeholder."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Analyse thumbnails but don’t write changes to the database.",
        )

    def handle(self, *args, **opts):
        dry_run   = opts["dry_run"]
        touched   = 0
        analysed  = 0

        for movie in Movie.objects.all():
            analysed += 1
            url = (movie.thumbnail_url or "").strip()
            replace = False

            if not url:
                replace = True
                reason  = "missing"
            else:
                img = load_image(url)
                if img is None:
                    replace = True
                    reason  = "unreadable"
                elif is_mostly_black(img):
                    replace = True
                    reason  = "mostly-black"
                elif _hash(img) in KNOWN_BAD_HASHES:
                    replace = True
                    reason  = "known-bad hash"

            if replace:
                self.stdout.write(f"→ {movie.title[:45]:45}  –  {reason}")
                if not dry_run:
                    movie.thumbnail_url = PLACEHOLDER_URL
                    movie.save(update_fields=["thumbnail_url"])
                touched += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Analysed {analysed} movies – updated {touched} thumbnails."
                + (" (dry run)" if dry_run else "")
            )
        )
