from django.urls import path
from . import views

urlpatterns = [
    path('', views.MovieList.as_view(), name='movie-list'),

    # Movie details (slug-based)
    path('<slug:slug>/', views.MovieDetailSlug.as_view(), name='movie-detail-slug'),

    # Hero movies
    path('hero-movies/', views.HeroCarouselMovies.as_view(), name='hero-carousel'),

    # Favorites (still using ID)
    path('favorites/', views.favorite_list, name='favorites'),
    path('favorites/add/', views.add_favorite, name='add-favorite'),
    path('favorites/<int:movie_id>/remove/', views.remove_favorite, name='remove-favorite'),

    # Watch Later (still using ID)
    path('watchlater/', views.watchlater_list, name='watchlater-list'),
    path('watchlater/add/', views.add_watchlater, name='watchlater-add'),
    path('watchlater/<int:movie_id>/', views.remove_watchlater, name='watchlater-remove'),

    # Progress (slug-based for frontend compatibility)
    path('progress/update/<slug:slug>/', views.update_progress_slug, name='progress-update-slug'),

    # Comments (slug-based)
    path('<slug:slug>/comments/', views.CommentListCreateSlug.as_view()),
    path('comments/<int:pk>/', views.CommentDelete.as_view()),
]
