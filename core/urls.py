from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                  path('', include('theme.urls')),
                  path('', include('panel.urls')),
                  path('', include('flights.urls')),
                  path('', include('appuser.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
