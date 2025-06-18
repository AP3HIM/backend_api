# movies/management/commands/colorize_all_thumbs.py
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps
from django.core.management.base import BaseCommand

THUMB_DIR   = Path("media/movies/thumbnails")
SATURATION  = 4.5                         # stronger pop
FLAG_SUFFIX = ".col"                      # 0-byte flag file

def is_grayscale(im: Image.Image) -> bool:
    r, g, b = im.split()
    spread  = max(
        r.getextrema()[1] - r.getextrema()[0],
        g.getextrema()[1] - g.getextrema()[0],
        b.getextrema()[1] - b.getextrema()[0],
    )
    return spread < 120                    # tweak if needed

def colorize(path: Path) -> bool:
    flag = path.with_suffix(path.suffix + FLAG_SUFFIX)
    if flag.exists():
        return False                      # already done once

    try:
        im = Image.open(path).convert("RGB")
        if not is_grayscale(im):
            flag.touch()                  # mark as checked
            return False

        im = ImageOps.autocontrast(im)    # brighten very dark frames
        ImageEnhance.Color(im).enhance(SATURATION).save(path, quality=92)
        flag.touch()
        return True
    except Exception as exc:
        print(f"   {path.name}: {exc}")
        return False

class Command(BaseCommand):
    help = "Artificially colourises dull / grayscale thumbnails."

    def handle(self, *args, **opts):
        thumbs   = list(THUMB_DIR.glob("*.jpg"))
        touched  = 0
        for tp in thumbs:
            if colorize(tp):
                print(f"   {tp.name} CHECK")
                touched += 1

        self.stdout.write(
            self.style.SUCCESS(f"\nDone – {touched}/{len(thumbs)} updated.")
        )
