from django.contrib import admin
from django.urls import path, include   
from accounts.views import VerifiedEmailTokenView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('movies.urls')),
    path('api/', include('accounts.urls')),
    path("api/auth/", include("allauth.urls")),
    path("api/token/", VerifiedEmailTokenView.as_view(), name="token_obtain_pair"),
    path("accounts/", include("allauth.urls")),  # Handles confirm-email/<key> with Allauth default view
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
