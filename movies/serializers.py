from rest_framework import serializers
from .models import Movie, Favorite, WatchLater, PlaybackProgress, Comment

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class FavoriteSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), source='movie', write_only=True
    )

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'movie', 'movie_id']
        read_only_fields = ['user']

class WatchLaterSerializer(serializers.ModelSerializer):
    class Meta:
        model  = WatchLater
        fields = ["id", "movie", "added_at"]        # “movie” returns its id by default

class PlaybackProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PlaybackProgress
        fields = ["id", "movie", "position", "updated_at"]
        read_only_fields = ["id", "updated_at"]

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model  = Comment
        fields = ["id", "user_name", "user", "movie", "text",
                  "rating", "created_at"]
        read_only_fields = ["id", "user", "movie", "created_at", "user_name"]