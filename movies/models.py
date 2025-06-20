from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    title = models.CharField(max_length=500, unique=True)
    overview = models.TextField(blank=True)
    year = models.IntegerField(blank=True, null=True)
    genre = models.CharField(max_length=150, blank=True)
    video_url = models.URLField(max_length=500)  # Direct .mp4 or similar
    thumbnail_url = models.URLField(max_length=500, blank=True)
    runtime_minutes = models.IntegerField(blank=True, null=True)
    archive_identifier = models.CharField(max_length=600, unique=True, null=True)
    is_featured = models.BooleanField(default=False)  # NEW
    views = models.IntegerField(default=0)  # NEW
    is_public_domain = models.BooleanField(default=True)
    is_hero = models.BooleanField(default=False)  # ✅ New field



    def __str__(self):
        return self.title

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="movie_favorites")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'movie')  # Prevent duplicates

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"
    

class WatchLater(models.Model):
    user  = models.ForeignKey(User,   on_delete=models.CASCADE, related_name="movie_watchlist")
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")          # one entry per user/movie
        ordering = ["-added_at"]                     # newest first

    def __str__(self):
        return f"{self.user.username} → {self.movie.title}"

#  ⬇︎ add at the bottom of the file
class PlaybackProgress(models.Model):
    user      = models.ForeignKey(User,   on_delete=models.CASCADE,
                                  related_name="movie_progress")
    movie     = models.ForeignKey(Movie,  on_delete=models.CASCADE)
    position  = models.PositiveIntegerField(default=0)   # seconds
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "movie")
        ordering        = ["-updated_at"]

    def __str__(self):
        mm = self.position // 60
        ss = self.position % 60
        return f"{self.user.username} → {self.movie.title} @ {mm}:{ss:02}"
    
# -- add after PlaybackProgress --
class Comment(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name="movie_comments")
    movie     = models.ForeignKey(Movie, on_delete=models.CASCADE,
                                  related_name="comments")
    text      = models.TextField(max_length=2_000)
    rating    = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5 stars
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} → {self.movie.title} ({self.rating or '-'}★)"



    
#python manage.py makemigrations
#python manage.py migrate
