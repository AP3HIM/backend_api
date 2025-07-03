from django.urls import path
from . import views
from movies.sitemaps import MovieSitemap, StaticViewSitemap, GenreSitemap
from django.contrib.sitemaps.views import sitemap

sitemaps = {
    'movies': MovieSitemap,
    'static': StaticViewSitemap,
    'genres': GenreSitemap,
}

urlpatterns = [
    path('', views.MovieList.as_view(), name='movie-list'),
    path('<slug:slug>/', views.MovieDetailSlug.as_view(), name='movie-detail-slug'),  # NEW
    path('<int:pk>/', views.MovieDetail.as_view(), name='movie-detail'),
    path('fetch-archive/', views.fetch_archive_movies, name='fetch-archive'),
    path('increment-view/<int:movie_id>/', views.increment_view, name='increment-view'),
    path('hero-movies/', views.HeroCarouselMovies.as_view(), name='hero-carousel'),

    # Favorites
    path('favorites/', views.favorite_list, name='favorites'),
    path('favorites/add/', views.add_favorite, name='add-favorite'),
    path('favorites/<int:movie_id>/remove/', views.remove_favorite, name='remove-favorite'),

    # Watch Later
    path('watchlater/', views.watchlater_list, name='watchlater-list'),
    path('watchlater/add/', views.add_watchlater, name='watchlater-add'),
    path('watchlater/<int:movie_id>/', views.remove_watchlater, name='watchlater-remove'),

    # Progress
    path('progress/', views.progress_list, name='progress-list'),
    path('progress/update/', views.update_progress, name='progress-update'),

    # Comments
    path('<int:movie_id>/comments/', views.CommentListCreate.as_view()),
    path('comments/<int:pk>/', views.CommentDelete.as_view()),

    #Sitemaps
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap")
]
