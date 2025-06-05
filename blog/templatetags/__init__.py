from django import template
from django.conf import settings
from django.utils import translation

register = template.Library()

@register.inclusion_tag('blog/language_selector.html', takes_context=True)
def language_selector(context):
    """
    Affiche un sélecteur de langue
    """
    request = context['request']
    current_language = translation.get_language()
    
    languages = []
    for code, name in settings.LANGUAGES:
        languages.append({
            'code': code,
            'name': name,
            'is_current': code == current_language,
            'url': f"{request.path}?lang={code}"
        })
    
    return {
        'languages': languages,
        'current_language': current_language,
        'request': request
    }

@register.simple_tag
def get_current_language():
    """
    Retourne la langue actuellement active
    """
    return translation.get_language()

@register.filter
def translate_if_exists(value, language=None):
    """
    Traduit une valeur si la traduction existe
    """
    if language is None:
        language = translation.get_language()
    
    # Dictionnaire simple de traductions pour les valeurs communes
    translations = {
        'fr': {
            'Home': 'Accueil',
            'Articles': 'Articles',
            'Categories': 'Catégories',
            'Login': 'Se connecter',
            'Logout': 'Se déconnecter',
            'Profile': 'Profil',
            'Add Article': 'Ajouter un article',
            'Edit': 'Modifier',
            'Delete': 'Supprimer',
            'Save': 'Sauvegarder',
            'Cancel': 'Annuler',
            'Back': 'Retour',
            'Next': 'Suivant',
            'Previous': 'Précédent',
        },
        'en': {
            'Accueil': 'Home',
            'Articles': 'Articles',
            'Catégories': 'Categories',
            'Se connecter': 'Login',
            'Se déconnecter': 'Logout',
            'Profil': 'Profile',
            'Ajouter un article': 'Add Article',
            'Modifier': 'Edit',
            'Supprimer': 'Delete',
            'Sauvegarder': 'Save',
            'Annuler': 'Cancel',
            'Retour': 'Back',
            'Suivant': 'Next',
            'Précédent': 'Previous',
        }
    }
    
    if language in translations and value in translations[language]:
        return translations[language][value]
    
    return value
