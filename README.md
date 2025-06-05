# 🚗 Blog Automobile Django

Une application de blog moderne dédiée à l'automobile avec support multilingue, système de rôles avancé et intégration ChatGPT/DALL-E.

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Système de rôles](#-système-de-rôles)
- [API ChatGPT](#-api-chatgpt)
- [Internationalisation](#-internationalisation)
- [Commandes de gestion](#-commandes-de-gestion)
- [Structure du projet](#-structure-du-projet)
- [Dépannage](#-dépannage)
- [Contribution](#-contribution)

## 🚀 Fonctionnalités

### Fonctionnalités principales
- **Blog automobile complet** : Articles, catégories, commentaires
- **Support multilingue** : Français, Anglais, Espagnol
- **Système de rôles granulaire** : 5 niveaux d'utilisateurs avec permissions spécifiques
- **Intégration ChatGPT** : Assistant IA pour la rédaction d'articles
- **Génération d'images DALL-E** : Création d'images automatisée
- **Moteur de recommandations** : Suggestions personnalisées d'articles
- **Interface administrative avancée** : Gestion complète des utilisateurs et contenus
- **Design responsive** : Compatible mobile et desktop
- **Mode sombre/clair** : Interface adaptative

### Fonctionnalités techniques
- **Base de données PostgreSQL** : Stockage robuste et performant
- **Middleware personnalisés** : Recommandations et gestion des langues
- **Système de logging** : Traçabilité complète des actions
- **Gestion des médias** : Upload et stockage d'images
- **Sécurité avancée** : Authentification, autorisation et protection CSRF
- **Tests automatisés** : Framework de tests intégré

## 📋 Prérequis

### Logiciels requis
- **Python 3.8+** (testé avec Python 3.13)
- **PostgreSQL 12+** 
- **Git** (pour le clonage du repository)
- **pip** (gestionnaire de packages Python)

### Comptes de service (optionnel)
- **Compte OpenAI** : Pour les fonctionnalités ChatGPT et DALL-E
  - Clé API OpenAI avec accès aux modèles GPT et DALL-E

## 🛠 Installation

### 1. Cloner le projet

```bash
git clone <url-du-repository>
cd mon_projet
```

### 2. Créer un environnement virtuel

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Si le fichier `requirements.txt` n'existe pas, installez manuellement :

```bash
pip install django==5.2.1
pip install psycopg2-binary
pip install pillow
pip install openai
pip install requests
```

### 4. Configuration de PostgreSQL

1. **Installer PostgreSQL** sur votre système
2. **Créer une base de données** :

```sql
CREATE DATABASE blog_db;
CREATE USER postgres WITH ENCRYPTED PASSWORD 'admin';
GRANT ALL PRIVILEGES ON DATABASE blog_db TO postgres;
```

### 5. Configuration des variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# Base de données
DB_NAME=blog_db
DB_USER=postgres
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=django-insecure-zoi1%*+vx_wtr2%x(rz@ue_k1_@#3qo3t=8wr^rxfkc!#9_eb5
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI (optionnel)
OPENAI_API_KEY=your_openai_api_key_here
```

## ⚙️ Configuration

### 1. Migrations de base de données

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Initialisation du système de rôles

```bash
python manage.py init_roles --create-admin
```

Cette commande :
- Crée les groupes de permissions
- Initialise les rôles utilisateur
- Crée un compte administrateur (admin/admin123)

### 3. Compilation des traductions

```bash
python manage.py compilemessages
```

### 4. Collecte des fichiers statiques

```bash
python manage.py collectstatic
```

### 5. Création d'un superutilisateur (optionnel)

```bash
python manage.py createsuperuser
```

## 🚀 Utilisation

### Démarrage du serveur

```bash
python manage.py runserver
```

L'application sera accessible à : `http://localhost:8000`

### URLs principales

- **Accueil** : `http://localhost:8000/`
- **Administration Django** : `http://localhost:8000/admin/`
- **Gestion des utilisateurs** : `http://localhost:8000/fr/gestion-utilisateurs/`
- **ChatGPT** : `http://localhost:8000/fr/chatgpt/`
- **Statistiques** : `http://localhost:8000/fr/statistiques-roles/`

### Comptes par défaut

Après l'initialisation :
- **Administrateur** : `admin` / `admin123`

## 👥 Système de rôles

L'application dispose de 5 niveaux d'utilisateurs avec des permissions granulaires :

### 1. **Lecteur** (par défaut)
- Lecture des articles
- Ajout de commentaires
- Gestion de son profil

### 2. **Rédacteur**
- Toutes les permissions du Lecteur
- Création et édition de ses propres articles
- Publication d'articles
- Accès au ChatGPT pour l'aide à la rédaction

### 3. **Modérateur**
- Toutes les permissions du Rédacteur
- Modération des commentaires
- Suppression de commentaires inappropriés
- Gestion des signalements

### 4. **Éditeur**
- Toutes les permissions du Modérateur
- Édition de tous les articles
- Gestion des catégories
- Accès aux statistiques
- Publication d'articles pour d'autres auteurs

### 5. **Administrateur**
- Toutes les permissions
- Gestion complète des utilisateurs
- Modification des rôles et statuts
- Accès à l'administration Django
- Gestion des paramètres système

## 🤖 API ChatGPT

### Configuration

1. **Obtenir une clé API OpenAI** sur [platform.openai.com](https://platform.openai.com)

2. **Ajouter la clé** dans le fichier `.env` :
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Fonctionnalités disponibles

#### Chat interactif
- Conversation en temps réel avec ChatGPT
- Suggestions d'articles automobiles
- Aide à la rédaction

#### Génération d'images
- Création d'images avec DALL-E
- Option activable pour chaque message
- Téléchargement des images générées

#### Génération d'articles complets
- Création automatique d'articles structurés
- Génération de titre, contenu et image
- Publication directe dans le blog

### Utilisation

1. **Connectez-vous** avec un compte ayant les permissions suffisantes
2. **Accédez à** `/fr/chatgpt/`
3. **Tapez votre message** dans la zone de saisie
4. **Activez l'option image** si souhaitée
5. **Cliquez sur Envoyer**

## 🌍 Internationalisation

L'application supporte 3 langues :

### Langues disponibles
- **Français** (fr) - langue par défaut
- **Anglais** (en)
- **Espagnol** (es)

### Gestion des traductions

#### Mise à jour des traductions
```bash
python manage.py makemessages -l fr -l en -l es
python manage.py compilemessages
```

#### Script de gestion personnalisé
```bash
# Mise à jour automatique
python manage_translations.py update

# Ajout manuel d'une traduction
python manage_translations.py add "Hello" "Bonjour" "Hola"
```

#### Changement de langue
Les utilisateurs peuvent changer de langue via :
- Le sélecteur de langue dans l'interface
- L'URL : `/fr/`, `/en/`, `/es/`
- Les paramètres de profil

## 🔧 Commandes de gestion

### Système de rôles

```bash
# Initialiser le système complet
python manage.py init_roles --create-admin

# Assigner un rôle à un utilisateur
python manage.py assign_role <username> <role>

# Lister les rôles disponibles
python manage.py assign_role --list-roles
```

### Traductions

```bash
# Compiler toutes les traductions
python manage.py compilemessages

# Mettre à jour les fichiers de traduction
python manage.py makemessages -l fr -l en -l es
```

### Base de données

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Vider la base de données
python manage.py flush
```

### Utilitaires

```bash
# Collecter les fichiers statiques
python manage.py collectstatic

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer les tests
python manage.py test
```

## 📁 Structure du projet

```
mon_projet/
├── manage.py                 # Point d'entrée Django
├── requirements.txt          # Dépendances Python
├── .env                     # Variables d'environnement
├── .gitignore              # Fichiers ignorés par Git
├── manage_translations.py   # Utilitaire de traductions
├── compile_translations.py  # Compilation des traductions
├── db.sqlite3              # Base de données (si SQLite)
├── django.log              # Fichier de logs
│
├── mon_projet/             # Configuration principale
│   ├── __init__.py
│   ├── settings.py         # Paramètres Django
│   ├── urls.py            # URLs principales
│   ├── wsgi.py            # Interface WSGI
│   └── asgi.py            # Interface ASGI
│
├── blog/                   # Application principale
│   ├── __init__.py
│   ├── admin.py           # Configuration admin Django
│   ├── apps.py            # Configuration de l'app
│   ├── models.py          # Modèles de données
│   ├── views.py           # Vues principales
│   ├── views_roles.py     # Vues de gestion des rôles
│   ├── urls.py            # URLs de l'application
│   ├── forms.py           # Formulaires Django
│   ├── decorators.py      # Décorateurs personnalisés
│   ├── language_middleware.py      # Middleware de langue
│   ├── recommendation_middleware.py # Middleware de recommandations
│   ├── tests.py           # Tests unitaires
│   │
│   ├── management/        # Commandes de gestion
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── init_roles.py     # Initialisation des rôles
│   │       └── assign_role.py    # Attribution des rôles
│   │
│   ├── migrations/        # Migrations de base de données
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   └── ...
│   │
│   ├── static/blog/       # Fichiers statiques
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │
│   ├── templates/blog/    # Templates HTML
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── chatgpt.html
│   │   ├── gestion_utilisateurs.html
│   │   └── ...
│   │
│   └── templatetags/      # Tags de template personnalisés
│       ├── __init__.py
│       ├── date_tags.py
│       └── language_tags.py
│
└── locale/                # Fichiers de traductions
    ├── fr/LC_MESSAGES/
    ├── en/LC_MESSAGES/
    └── es/LC_MESSAGES/
```

## 🔍 Dépannage

### Erreurs communes

#### 1. Erreur de base de données
```
django.db.utils.OperationalError: could not connect to server
```
**Solution** : Vérifiez que PostgreSQL est démarré et que les paramètres de connexion sont corrects dans `settings.py`.

#### 2. Erreur de migrations
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```
**Solution** :
```bash
python manage.py migrate --fake-initial
```

#### 3. Erreur de permissions
```
PermissionDenied: Vous n'avez pas les permissions nécessaires
```
**Solution** : Vérifiez le rôle de l'utilisateur et réinitialisez les permissions si nécessaire :
```bash
python manage.py init_roles
```

#### 4. Erreur OpenAI
```
AuthenticationError: Incorrect API key provided
```
**Solution** : Vérifiez que la clé API OpenAI est correctement configurée dans le fichier `.env`.

#### 5. Erreur de traductions
```
CommandError: Can't find msguniq. Make sure you have GNU gettext tools
```
**Solution** : Installez GNU gettext :
- **Windows** : Téléchargez depuis [mlocati.github.io/articles/gettext-iconv-windows.html](https://mlocati.github.io/articles/gettext-iconv-windows.html)
- **Ubuntu/Debian** : `sudo apt-get install gettext`
- **macOS** : `brew install gettext`

### Logs et debugging

#### Consulter les logs
```bash
# Logs Django
tail -f django.log

# Logs du serveur de développement
python manage.py runserver --verbosity=2
```

#### Mode debug
Activez le mode debug dans `.env` :
```env
DEBUG=True
```

#### Tests
```bash
# Lancer tous les tests
python manage.py test

# Tests spécifiques
python manage.py test blog.tests.TestModels
```

### Réinitialisation complète

En cas de problème majeur :

```bash
# 1. Supprimer la base de données
dropdb blog_db
createdb blog_db

# 2. Supprimer les migrations
rm blog/migrations/0*.py

# 3. Recréer les migrations
python manage.py makemigrations
python manage.py migrate

# 4. Réinitialiser le système
python manage.py init_roles --create-admin
```

## 🤝 Contribution

### Développement

1. **Forkez** le projet
2. **Créez une branche** pour votre fonctionnalité
3. **Commitez** vos changements
4. **Testez** votre code
5. **Soumettez** une Pull Request

### Standards de code

- **PEP 8** pour le style Python
- **Commentaires** en français
- **Tests unitaires** pour toute nouvelle fonctionnalité
- **Documentation** des nouvelles APIs

### Structure des commits

```
type(scope): description

[corps du message]

[footer]
```

Exemples :
- `feat(auth): ajouter l'authentification à deux facteurs`
- `fix(chatgpt): corriger l'erreur de timeout API`
- `docs(readme): mettre à jour la documentation d'installation`

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👨‍💻 Auteur

Développé avec ❤️ pour la communauté automobile.

---

## 📞 Support

Pour toute question ou problème :

1. **Consultez** la section [Dépannage](#-dépannage)
2. **Vérifiez** les [issues GitHub](lien-vers-issues)
3. **Ouvrez** une nouvelle issue si nécessaire

---

**Version** : 1.0.0  
**Dernière mise à jour** : Juin 2025
#   d j a n g o  
 