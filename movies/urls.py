from django.urls import path
from . import views

urlpatterns = [
    path('movies/', views.MovieList.as_view(), name='movie-list'),
    path('movies/<int:pk>/', views.MovieDetail.as_view(), name='movie-detail'),
    path('movies/import/', views.import_movies_view, name='import-movies'),
    path('movies/fetch-archive/', views.fetch_archive_movies, name='fetch-archive'),
    path('increment-view/<int:movie_id>/', views.increment_view, name='increment-view'),
     path('hero-movies/', views.HeroCarouselMovies.as_view(), name='hero-carousel'),

    # Split into separate endpoints for GET and POST
    path('favorites/', views.favorite_list, name='favorites'),  # GET only
    path('favorites/add/', views.add_favorite, name='add-favorite'),  # POST only
    path('favorites/<int:movie_id>/remove/', views.remove_favorite, name='remove-favorite'),  # DELETE

    path("watchlater/",                 views.watchlater_list,   name="watchlater-list"),   # GET
    path("watchlater/add/",             views.add_watchlater,    name="watchlater-add"),    # POST
    path("watchlater/<int:movie_id>/",  views.remove_watchlater, name="watchlater-remove"), # DELETE

    path("progress/",        views.progress_list,   name="progress-list"),   # GET
    path("progress/update/", views.update_progress, name="progress-update"), # POST

    path("movies/<int:movie_id>/comments/", views.CommentListCreate.as_view()),
    path("comments/<int:pk>/",              views.CommentDelete.as_view()),

    path("make-me-staff/", views.make_me_staff, name="make-me-staff"),
]
