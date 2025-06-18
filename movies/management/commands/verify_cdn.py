import os
import requests
from django.core.management.base import BaseCommand
from movies.models import Movie
import time
from urllib.parse import urljoin # Import urljoin

# Ensure CDN_BASE_URL always ends with a slash for clean joining
CDN_BASE_URL = "https://cdn.papertigercinema.com/" 

class Command(BaseCommand):
    help = "Verify that video and thumbnail files exist on the CDN or their original source."

    def handle(self, *args, **kwargs):
        total = Movie.objects.count()
        passed = 0
        failed = []

        for i, movie in enumerate(Movie.objects.all()):
            # Print progress on the same line
            self.stdout.write(f"Checking Movie {movie.id} ({i+1}/{total})...", ending='\r')
            self.stdout.flush() 

            final_video_url = self.get_final_url(movie.video_url)
            final_thumb_url = self.get_final_url(movie.thumbnail_url)

            video_ok = True
            if final_video_url: # Only check if a URL exists
                video_ok = self.check_url(final_video_url)
            else: # If URL is empty, consider it "missing" for now or handle as needed
                video_ok = False 

            thumb_ok = True
            if final_thumb_url: # Only check if a URL exists
                thumb_ok = self.check_url(final_thumb_url)
            else: # If URL is empty, consider it "missing" for now or handle as needed
                thumb_ok = False

            if video_ok and thumb_ok:
                passed += 1
            else:
                failed.append((movie.id, final_video_url if not video_ok else None, final_thumb_url if not thumb_ok else None))
            
            time.sleep(1) # Keep this delay for Archive.org stability

        self.stdout.write("\n") # Print a newline character after the loop is done to clear the progress line
        self.stdout.write(f"\nCDN Verification Complete\n")
        self.stdout.write(f"✔ Passed: {passed}")
        self.stdout.write(f"❌ Failed: {len(failed)}")

        for movie_id, bad_video, bad_thumb in failed:
            self.stdout.write(f" - Movie {movie_id}:")
            if bad_video:
                self.stdout.write(f"     ⚠ Missing video: {bad_video}")
            if bad_thumb:
                self.stdout.write(f"     ⚠ Missing thumbnail: {bad_thumb}")

    def get_final_url(self, url):
        """
        Constructs the final URL.
        If URL is absolute (http/https), returns it as is.
        Otherwise, assumes it's a relative path for CDN_BASE_URL and uses urljoin.
        """
        if not url:
            return None
        
        # Check if the URL already starts with http:// or https:// (absolute URL)
        if url.startswith("http://") or url.startswith("https://"):
            return url
        else:
            # Use urljoin for robust path joining with the CDN base URL
            return urljoin(CDN_BASE_URL, url) 

    def check_url(self, url):
        try:
            r = requests.head(url, timeout=5)
            # Consider 200 (OK), 301 (Moved Permanently), 302 (Found) as valid
            return r.status_code in [200, 301, 302] 
        except requests.exceptions.RequestException as e:
            # Print errors immediately for debugging
            self.stdout.write(self.style.ERROR(f"\nError checking {url}: {e}"), ending='\n') 
            return False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nUnexpected error for {url}: {e}"), ending='\n')
            return False
