# movies/management/commands/remove_non_public_domain.py

from django.core.management.base import BaseCommand
from movies.models import Movie

class Command(BaseCommand):
    help = "Delete movies that are likely not in the public domain based on year and basic rules."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show which movies would be deleted without actually deleting them."
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        deleted = 0
        total   = 0

        for movie in Movie.objects.exclude(year=None):
            total += 1
            year = movie.year

            # Flag movies as NOT public domain if:
            is_non_public = (
                year >= 1964 or                 # Likely copyrighted if 1964+
                (1929 <= year <= 1963)          # Only public if not renewed, which we can't verify
            )

            if is_non_public:
                self.stdout.write(f"→ {movie.title} ({year}) – deleted")
                deleted += 1
                if not dry_run:
                    movie.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nChecked {total} movies — {deleted} {'would be' if dry_run else 'were'} deleted."
            )
        )
