from django.core.management.base import BaseCommand
from movies.models import Movie
from pathlib import Path
from PIL import Image, ImageEnhance
import os

THUMB_DIR = "media/movies/thumbnails"

def colorize_image(path):
    try:
        im = Image.open(path).convert("RGB")

        # simple check: is image nearly grayscale?
        if im.getextrema()[0][1] - im.getextrema()[0][0] < 30:
            enhancer = ImageEnhance.Color(im)
            im_colored = enhancer.enhance(2.5)  # fake some saturation
            im_colored.save(path)
            return True
        return False
    except Exception as e:
        print("    failed:", e)
        return False

class Command(BaseCommand):
    help = "Adds artificial color to grayscale thumbnails of featured movies."

    def handle(self, *args, **options):
        featured = Movie.objects.filter(is_featured=True)
        print(f"Checking {featured.count()} featured movie thumbnails...")

        count = 0
        for movie in featured:
            filename = Path(THUMB_DIR) / f"{movie.id}.jpg"
            if not filename.exists():
                print(f"    skipping {movie.id} – no thumb")
                continue
            if colorize_image(filename):
                print(f"     colorized: {movie.title}")
                count += 1

        print(f"\nDone! {count} thumbnails colorized.")
