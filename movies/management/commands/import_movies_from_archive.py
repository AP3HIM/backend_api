# movies/management/commands/import_movies_from_archive.py

from django.core.management.base import BaseCommand
import requests
from movies.models import Movie
import time

class Command(BaseCommand):
    help = "Imports movies from Internet Archive (only ≥45 min, with a real thumbnail), grouped by genre."

    def handle(self, *args, **options):
        def parse_runtime(runtime_raw):
            """
            Convert a runtime string (e.g. "01:30:00", "90:00", or numeric) into total minutes.
            """
            try:
                if isinstance(runtime_raw, str) and ":" in runtime_raw:
                    parts = list(map(int, runtime_raw.split(":")))
                    if len(parts) == 3:      # "HH:MM:SS"
                        hours, minutes, _ = parts
                        return hours * 60 + minutes
                    elif len(parts) == 2:    # "MM:SS"
                        minutes, _ = parts
                        return minutes
                return int(float(runtime_raw))
            except Exception:
                return None

        def is_non_movie(title, overview):
            """
            Skip items that look like trailers, interviews, episodes, etc.
            """
            checks = ["trailer", "interview", "episode", "tv", "pilot", "behind the scenes"]
            content = f"{title} {overview}".lower()
            return any(term in content for term in checks)

        # List of genres to import—adjust as desired
        GENRES = [
            "Horror",
            "Comedy",
            "Drama",
            "Sci-Fi",
            "Action",
            "Romance",
            "Western",
            "Thriller",
        ]
        '''
        [
        "Action",
        "Adventure",
        "Animation",
        "Biography",
        "Comedy",
        "Crime",
        "Documentary",
        "Drama",
        "Family",
        "Fantasy",
        "Film Noir",
        "Historical",
        "Horror",
        "Independent",
        "Musical",
        "Mystery",
        "Romance",
        "Science Fiction", # Or just "Sci-Fi" if you prefer
        "Short Film",
        "Silent Film",
        "Sport",
        "Thriller",
        "War",
        "Western",
        "Cult Classic", # Optional, but good for niche appeal
        ]
        '''
        max_pages = 20  # Number of pages per genre to fetch (50 items per page)
        for genre in GENRES:
            page = 1
            imported_count = 0
            self.stdout.write(self.style.NOTICE(f"=== Importing genre: {genre} ==="))

            while page <= max_pages:
                # Build the advancedsearch query for this genre + feature_films + mediatype
                query = {
                    "q": f'collection:(feature_films) AND mediatype:(movies) AND subject:("{genre}")',
                    "fl[]": ["identifier", "title", "description", "year"],
                    "rows": 50,
                    "page": page,
                    "output": "json",
                }

                try:
                    resp = requests.get(
                        "https://archive.org/advancedsearch.php",
                        params=query,
                        timeout=15
                    )
                    resp.raise_for_status()
                    docs = resp.json().get("response", {}).get("docs", [])
                    if not docs:
                        break
                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(f"[{genre}][page {page}] Search request failed: {e}")
                    )
                    break

                for doc in docs:
                    identifier = doc.get("identifier")
                    title = doc.get("title", "Untitled")
                    overview = doc.get("description", "No description.")[:1000]

                    try:
                        year = int(doc.get("year"))
                    except (TypeError, ValueError):
                        year = None

                    # Skip if this identifier is already in the database
                    if identifier and Movie.objects.filter(archive_identifier=identifier).exists():
                        continue

                    # Skip if a movie with this title already exists (avoid unique title clash)
                    if Movie.objects.filter(title=title).exists():
                        continue

                    # Fetch metadata JSON (for runtime, files, etc.)
                    metadata_url = f"https://archive.org/metadata/{identifier}"
                    try:
                        meta_res = requests.get(metadata_url, timeout=15)
                        meta_res.raise_for_status()
                    except Exception:
                        self.stderr.write(
                            self.style.ERROR(f"[{genre}] Could not fetch metadata for {identifier} ({title})")
                        )
                        continue

                    metadata = meta_res.json()
                    files = metadata.get("files", [])
                    runtime_raw = metadata.get("metadata", {}).get("runtime")

                    # — Find a video file URL
                    video_url = ""
                    for f in files:
                        name = f.get("name", "").lower()
                        if name.endswith((".mp4", ".webm", ".mkv", ".avi", ".ogv")):
                            video_url = f"https://archive.org/download/{identifier}/{f['name']}"
                            break
                    if not video_url:
                        self.stderr.write(
                            self.style.WARNING(f"[{genre}] No video file found for {title}")
                        )
                        continue

                    # — Find a thumbnail URL
                    thumbnail_url = None
                    for f in files:
                        name = f.get("name", "").lower()
                        if name.endswith((".jpg", ".png")):
                            thumbnail_url = f"https://archive.org/download/{identifier}/{f['name']}"
                            break
                    if not thumbnail_url:
                        self.stderr.write(
                            self.style.WARNING(f"[{genre}] No thumbnail candidate for {title}")
                        )
                        continue

                    # — Parse runtime into minutes
                    runtime_minutes = parse_runtime(runtime_raw) if runtime_raw else None
                    if runtime_minutes is None:
                        self.stdout.write(
                            self.style.WARNING(f"[{genre}] Skipped (no runtime): {title}")
                        )
                        continue
                    if runtime_minutes < 45:
                        self.stdout.write(
                            self.style.WARNING(f"[{genre}] Skipped (too short <45 min): {title}")
                        )
                        continue

                    if is_non_movie(title, overview):
                        self.stdout.write(
                            self.style.WARNING(f"[{genre}] Skipped (non-movie): {title}")
                        )
                        continue

                    # Create the Movie record (only if title/identifier don't already exist)
                    movie, created = Movie.objects.get_or_create(
                        title=title,
                        defaults={
                            "overview": overview,
                            "year": year,
                            "genre": genre,
                            "video_url": video_url,
                            "thumbnail_url": thumbnail_url,
                            "runtime_minutes": runtime_minutes,
                            "archive_identifier": identifier,
                        },
                    )

                    if created:
                        imported_count += 1
                        self.stdout.write(self.style.SUCCESS(f"[{genre}] Imported: {title}"))
                    # else: already existed, skip without error

                page += 1
                time.sleep(1)  # brief pause to avoid hammering the API

            self.stdout.write(
                self.style.SUCCESS(f"=== Done with genre {genre}. Imported {imported_count} new movies. ===")
            )
