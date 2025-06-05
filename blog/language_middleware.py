from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class SimpleLanguageMiddleware(MiddlewareMixin):
    """
    Middleware simple pour gérer les langues sans gettext
    """
    
    def process_request(self, request):
        # Vérifier si une langue est demandée dans l'URL ou la session
        language = None
        
        # 1. Vérifier les paramètres GET (?lang=en)
        if 'lang' in request.GET:
            language = request.GET['lang']
        
        # 2. Vérifier la session
        elif hasattr(request, 'session') and 'django_language' in request.session:
            language = request.session['django_language']
        
        # 3. Vérifier les headers HTTP (Accept-Language)
        elif hasattr(request, 'META'):
            accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
            if 'fr' in accept_language.lower():
                language = 'fr'
            elif 'en' in accept_language.lower():
                language = 'en'
        
        # Utiliser la langue par défaut si aucune n'est trouvée
        if not language:
            language = settings.LANGUAGE_CODE
        
        # Vérifier que la langue est supportée
        supported_languages = [lang[0] for lang in settings.LANGUAGES]
        if language not in supported_languages:
            language = settings.LANGUAGE_CODE
        
        # Activer la langue
        translation.activate(language)
        
        # Sauvegarder dans la session
        if hasattr(request, 'session'):
            request.session['django_language'] = language
    
    def process_response(self, request, response):
        # Désactiver la traduction après la requête
        translation.deactivate()
        return response
