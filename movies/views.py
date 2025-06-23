from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.authentication import get_authorization_header
from django.core.management import call_command
from django.shortcuts import get_object_or_404
import requests, logging
from .models import Movie, Favorite, WatchLater, PlaybackProgress, Comment
from .serializers import MovieSerializer, FavoriteSerializer, WatchLaterSerializer, PlaybackProgressSerializer, CommentSerializer
from rest_framework.views import APIView


log = logging.getLogger("django.request")

def _dbg_show_auth(request):
    hdr = get_authorization_header(request).decode()
    log.warning("Auth-HDR [%s] %s", request.path, hdr or "NONE")

logging.basicConfig(level=logging.WARNING)   #  add once, near the top




@api_view(['POST'])
def import_movies_view(request):
    try:
        call_command('import_movies_from_archive')
        return Response({"status": "Import successful"})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


class MovieList(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]  # ← public
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['title', 'overview', 'genre']
    filterset_fields = ['genre', 'is_featured']
    ordering_fields = ['title', 'year']
    ordering = ['title']



class MovieDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    permission_classes = [AllowAny]  # ← public
    serializer_class = MovieSerializer

    def get_permissions(self):
            if self.request.method in ['PUT', 'PATCH', 'DELETE']:
                return [permissions.IsAdminUser()]
            return [permissions.AllowAny()]

class HeroCarouselMovies(APIView):
    def get(self, request):
        movies = Movie.objects.filter(is_hero=True).order_by('-year')  # optional: sort newest first
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def fetch_archive_movies(request):
    url = "https://archive.org/advancedsearch.php"
    params = {
        "q": 'collection:(feature_films) AND mediatype:(movies) AND format:(mpeg4)',
        "fl[]": ["identifier", "title", "description", "year", "creator"],
        "sort[]": "downloads desc",
        "rows": 20,
        "page": 1,
        "output": "json"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        movies_data = response.json()["response"]["docs"]

        results = []

        for movie in movies_data:
            identifier = movie.get("identifier")
            details_url = f"https://archive.org/metadata/{identifier}"
            details_response = requests.get(details_url)

            video_url = None
            thumbnail_url = None

            if details_response.status_code == 200:
                details = details_response.json()
                files = details.get("files", [])
                for f in files:
                    name = f.get("name", "")
                    if not video_url and name.endswith(".mp4"):
                        video_url = f"https://archive.org/download/{identifier}/{name}"
                    if not thumbnail_url and (name.endswith(".jpg") or name.endswith(".png")):
                        thumbnail_url = f"https://archive.org/download/{identifier}/{name}"

            results.append({
                "title": movie.get("title", "No Title"),
                "overview": movie.get("description", "No Description"),
                "year": movie.get("year"),
                "creator": movie.get("creator"),
                "identifier": identifier,
                "video_url": video_url,
                "thumbnail_url": thumbnail_url,
            })

        return Response(results)

    except requests.exceptions.RequestException as e:
        return Response({"error": "Network error", "details": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
    except Exception as e:
        return Response({"error": "Failed to fetch movies", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
def increment_view(request, movie_id):
    try:
        _dbg_show_auth(request)   
        movie = Movie.objects.get(id=movie_id)
        movie.views = (movie.views or 0) + 1
        movie.save()
        return Response({'success': True, 'views': movie.views})
    except Movie.DoesNotExist:
        return Response({'success': False, 'error': 'Movie not found'}, status=404)


# ----------------------------
# Favorite Views
# ----------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def favorite_list(request):
    _dbg_show_auth(request)   
    favorites = Favorite.objects.filter(user=request.user)
    serializer = FavoriteSerializer(favorites, many=True)
    return Response(serializer.data)

   
# views.py
@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def add_favorite(request):
    _dbg_show_auth(request)
    movie_id = request.data.get('movie_id')  # FIXED: now expecting 'movie_id'

    if not movie_id:
        return Response({'error': 'Movie ID is required'}, status=400)

    if Favorite.objects.filter(user=request.user, movie_id=movie_id).exists():
        return Response({'message': 'Already in favorites'}, status=400)

    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return Response({'error': 'Movie not found'}, status=404)

    Favorite.objects.create(user=request.user, movie=movie)
    return Response({'message': 'Added to favorites'})




@api_view(['DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def remove_favorite(request, movie_id):
    _dbg_show_auth(request)
    favorite = get_object_or_404(Favorite, user=request.user, movie__id=movie_id)
    favorite.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

#
#------------WatchLater--------
#
@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def watchlater_list(request):
    _dbg_show_auth(request)
    items = WatchLater.objects.filter(user=request.user).select_related("movie")
    ser   = WatchLaterSerializer(items, many=True, context={"request": request})
    return Response(ser.data)

@api_view(["POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def add_watchlater(request):
    _dbg_show_auth(request)
    movie_id = request.data.get("movie_id")
    if not movie_id:
        return Response({"error": "Movie ID required"}, status=400)

    if WatchLater.objects.filter(user=request.user, movie_id=movie_id).exists():
        return Response({"message": "Already in watch-later"}, status=400)

    WatchLater.objects.create(user=request.user, movie_id=movie_id)
    return Response({"message": "Added to watch-later"})

@api_view(["DELETE"])
@permission_classes([IsAuthenticatedOrReadOnly])
def remove_watchlater(request, movie_id):
    _dbg_show_auth(request)
    item = get_object_or_404(WatchLater, user=request.user, movie_id=movie_id)
    item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# -------------------------------------------------------------------
#  Playback progress
# -------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def progress_list(request):
    _dbg_show_auth(request)
    """Return all progress rows for the current user."""
    rows = PlaybackProgress.objects.filter(user=request.user).select_related("movie")
    ser  = PlaybackProgressSerializer(rows, many=True)
    return Response(ser.data)


@api_view(["POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def update_progress(request):
    _dbg_show_auth(request)
    """Create or update progress for one movie."""
    movie_id = request.data.get("movie_id")
    position = request.data.get("position")         # seconds (int)

    if movie_id is None or position is None:
        return Response({"error": "movie_id and position required"}, status=400)

    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return Response({"error": "Movie not found"}, status=404)

    row, _ = PlaybackProgress.objects.update_or_create(
        user=request.user,
        movie=movie,
        defaults={"position": int(position)},
    )
    return Response({"success": True, "position": row.position})


class CommentListCreate(generics.ListCreateAPIView):
    """
    GET  /api/movies/<movie_id>/comments/   – list
    POST /api/movies/<movie_id>/comments/   – create (auth required)
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(movie_id=self.kwargs["movie_id"])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,
                        movie_id=self.kwargs["movie_id"])


class CommentDelete(generics.DestroyAPIView):
    """
    DELETE /api/comments/<id>/    – owner only
    """
    queryset           = Comment.objects.all()
    serializer_class   = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_destroy(self, instance):
        # Optional: allow only the author (or staff) to delete
        if instance.user != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Not your comment.")
        super().perform_destroy(instance)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_me_staff(request):
    user = request.user
    user.is_staff = True
    user.save()
    return Response({"message": f"{user.username} is now staff."})
