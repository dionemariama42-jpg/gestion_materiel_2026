from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('comptes.urls')),
    path('materiel/', include('materiel.urls')),
    path('emprunts/', include('emprunts.urls')),
    path('cahier/', include('cahier.urls')),
    path('clubs/', include('clubs.urls')),
    path('dashboard/', include('dashboard.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)