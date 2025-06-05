from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# URLs non-internationalisées (pour i18n et admin)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
]

# URLs internationalisées (avec préfixe de langue)
urlpatterns += i18n_patterns(
    path('', include('blog.urls')),
    prefix_default_language=True  # Changé à True pour avoir un préfixe même pour la langue par défaut
)

# Ajout des fichiers statiques et media
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)