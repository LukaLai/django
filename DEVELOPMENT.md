# 🔧 Documentation développeur

Guide technique pour contribuer au projet et comprendre l'architecture.

## Architecture du projet

### Modèles de données

#### Article
- Titre, contenu, auteur
- Catégories (ManyToMany)
- Vues, date de création
- Image (optionnel)

#### ProfilUtilisateur
- Extension du modèle User Django
- Système de rôles à 5 niveaux
- Statuts (actif, inactif, suspendu, banni)
- Paramètres de notification

#### Système de recommandations
- Recommandations basées sur l'historique utilisateur
- Recommandations par session pour les anonymes
- Articles populaires en fallback

### Vues principales

#### Vues d'articles (`views.py`)
- `home` : Page d'accueil avec articles et recommandations
- `detail_article` : Vue détaillée d'un article
- `ajouter_article` : Création d'articles (rédacteurs+)

#### Vues de gestion (`views_roles.py`)
- `gestion_utilisateurs` : Administration des utilisateurs
- `modifier_role_utilisateur` : Changement de rôles (AJAX)
- `statistiques_roles` : Dashboard des statistiques

#### Vues ChatGPT (`views.py`)
- `chatgpt_view` : Interface de chat
- `chatgpt_api` : API pour communication avec OpenAI
- `generate_article_ai` : Génération automatique d'articles

### Décorateurs personnalisés

#### `@role_required(*roles)`
Vérifie si l'utilisateur a un des rôles spécifiés.

```python
@role_required('redacteur', 'editeur', 'administrateur')
def ma_vue(request):
    # Code accessible aux rédacteurs et plus
    pass
```

#### `@permission_required_custom(permission)`
Vérifie une permission spécifique via les méthodes du profil.

```python
@permission_required_custom('can_publish_articles')
def publier_article(request):
    # Code pour publier un article
    pass
```

#### `@author_or_role_required(*roles)`
Permet l'accès à l'auteur du contenu OU aux rôles spécifiés.

```python
@author_or_role_required('editeur', 'administrateur')
def modifier_article(request, article_id):
    # L'auteur ou un éditeur/admin peut modifier
    pass
```

## Système de rôles

### Hiérarchie des permissions

1. **Lecteur** : Permissions de base
2. **Rédacteur** : + Création d'articles
3. **Modérateur** : + Modération de commentaires
4. **Éditeur** : + Gestion de tous les articles et catégories
5. **Administrateur** : + Gestion des utilisateurs et système

### Permissions personnalisées

Définies dans `ProfilUtilisateur.Meta.permissions` :

- `can_moderate_comments`
- `can_manage_categories`
- `can_publish_articles`
- `can_edit_all_articles`
- `can_view_statistics`
- `can_manage_users`

### Méthodes de vérification

```python
# Dans le modèle ProfilUtilisateur
def peut_publier_articles(self):
    return self.role in ['redacteur', 'editeur', 'administrateur'] and self.statut == 'actif'

def peut_gerer_utilisateurs(self):
    return self.role == 'administrateur' and self.statut == 'actif'
```

## API ChatGPT

### Configuration

```python
# settings.py ou .env
OPENAI_API_KEY = "sk-..."
```

### Endpoints

#### `/fr/chatgpt/api/` (POST)
Envoi de messages à ChatGPT avec option génération d'image.

**Paramètres** :
```json
{
    "message": "Écris un article sur les voitures électriques",
    "generate_image": true
}
```

**Réponse** :
```json
{
    "success": true,
    "response": "Voici un article sur...",
    "image_url": "https://..."
}
```

#### `/fr/generate-article-ai/` (POST)
Génération complète d'un article avec titre, contenu et image.

**Paramètres** :
```json
{
    "prompt": "Article sur l'entretien automobile",
    "categories": [1, 2]
}
```

### Gestion des erreurs

```python
try:
    response = openai.ChatCompletion.create(...)
except openai.error.RateLimitError:
    return JsonResponse({'error': 'Limite de requêtes atteinte'})
except openai.error.AuthenticationError:
    return JsonResponse({'error': 'Clé API invalide'})
```

## Internationalisation

### Structure des fichiers

```
locale/
├── fr/LC_MESSAGES/
│   ├── django.po    # Traductions françaises
│   └── django.mo    # Traductions compilées
├── en/LC_MESSAGES/
│   ├── django.po    # Traductions anglaises
│   └── django.mo
└── es/LC_MESSAGES/
    ├── django.po    # Traductions espagnoles
    └── django.mo
```

### Workflow de traduction

1. **Marquer les chaînes** dans le code :
```python
from django.utils.translation import gettext_lazy as _

title = _("Titre de l'article")
```

2. **Extraire les chaînes** :
```bash
python manage.py makemessages -l fr -l en -l es
```

3. **Traduire** dans les fichiers `.po`

4. **Compiler** :
```bash
python manage.py compilemessages
```

### Script de gestion personnalisé

```bash
# Mise à jour automatique
python manage_translations.py update

# Ajout manuel
python manage_translations.py add "Hello" "Bonjour" "Hola"
```

## Middleware personnalisés

### RecommendationMiddleware

Ajoute des recommandations à chaque requête.

```python
class RecommendationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Logique de recommandations
        request.recommendations = get_recommendations(request.user)
        response = self.get_response(request)
        return response
```

### LocaleMiddleware

Gestion automatique de la langue basée sur l'URL et les préférences utilisateur.

## Tests

### Structure des tests

```python
# blog/tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Article, ProfilUtilisateur

class ArticleTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.com', 'pass')
        self.client = Client()

    def test_article_creation(self):
        # Test de création d'article
        pass

    def test_permissions(self):
        # Test des permissions
        pass
```

### Lancement des tests

```bash
# Tous les tests
python manage.py test

# Tests spécifiques
python manage.py test blog.tests.ArticleTestCase

# Avec couverture
coverage run --source='.' manage.py test
coverage report
```

## Déploiement

### Variables d'environnement de production

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=your-production-secret-key

# Base de données
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Fichiers statiques
STATIC_ROOT=/var/www/static/
MEDIA_ROOT=/var/www/media/

# Email
EMAIL_HOST=smtp.youremail.com
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=yourpassword
```

### Collecte des fichiers statiques

```bash
python manage.py collectstatic --noinput
```

### Configuration du serveur web

#### Nginx
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /var/www/static/;
    }

    location /media/ {
        alias /var/www/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Gunicorn
```bash
gunicorn mon_projet.wsgi:application --bind 127.0.0.1:8000
```

## Monitoring et logs

### Configuration des logs

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'blog': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Métriques importantes

- Nombre d'utilisateurs actifs
- Articles publiés par jour
- Utilisation de l'API ChatGPT
- Erreurs et temps de réponse

## Contribution

### Standards de code

1. **Style** : Suivre PEP 8
2. **Documentation** : Docstrings pour toutes les fonctions
3. **Tests** : Couverture > 80%
4. **Commits** : Messages explicites en français

### Workflow Git

```bash
# Nouvelle fonctionnalité
git checkout -b feat/nouvelle-fonctionnalite
git commit -m "feat: ajouter nouvelle fonctionnalité"
git push origin feat/nouvelle-fonctionnalite
# Créer une Pull Request
```

### Code review

Critères de validation :
- Tests passent
- Code documenté
- Pas de régressions
- Performance acceptable

---

*Cette documentation est maintenue par l'équipe de développement.*
