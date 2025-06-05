# 🚗 Blog Automobile Django

Une application de blog moderne dédiée à l'automobile avec support multilingue, système de rôles avancé et intégration ChatGPT/DALL-E.

## 📋 Table des matières

- [🚀 Fonctionnalités](#-fonctionnalités)
- [📋 Prérequis](#-prérequis)
- [🛠 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [🚀 Utilisation](#-utilisation)
- [👥 Système de rôles](#-système-de-rôles)
- [🤖 API ChatGPT](#-api-chatgpt)
- [🌍 Internationalisation](#-internationalisation)
- [🔧 Commandes de gestion](#-commandes-de-gestion)
- [📁 Structure du projet](#-structure-du-projet)
- [🔍 Dépannage](#-dépannage)
- [🤝 Contribution](#-contribution)

## 🚀 Fonctionnalités

### Fonctionnalités principales
✅ **Blog automobile complet** : Articles, catégories, commentaires  
✅ **Support multilingue** : Français, Anglais, Espagnol  
✅ **Système de rôles granulaire** : 5 niveaux d'utilisateurs  
✅ **Intégration ChatGPT** : Assistant IA pour la rédaction  
✅ **Génération d'images DALL-E** : Création d'images automatisée  
✅ **Moteur de recommandations** : Suggestions personnalisées  
✅ **Interface administrative avancée** : Gestion complète  
✅ **Design responsive** : Compatible mobile et desktop  
✅ **Mode sombre/clair** : Interface adaptative  

### Fonctionnalités techniques
🔧 **Base de données PostgreSQL** : Stockage robuste et performant  
🔧 **Middleware personnalisés** : Recommandations et gestion des langues  
🔧 **Système de logging** : Traçabilité complète des actions  
🔧 **Gestion des médias** : Upload et stockage d'images  
🔧 **Sécurité avancée** : Authentification et protection CSRF  
🔧 **Tests automatisés** : Framework de tests intégré  

## 📋 Prérequis

### Logiciels requis
- **Python 3.8+** (testé avec Python 3.13)
- **PostgreSQL 12+** 
- **Git** (pour le clonage du repository)
- **pip** (gestionnaire de packages Python)

### Comptes de service (optionnel)
- **Compte OpenAI** : Pour les fonctionnalités ChatGPT et DALL-E

## 🛠 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/votre-username/votre-repo.git
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

**Si `requirements.txt` n'existe pas :**

```bash
pip install django==5.2.1
pip install psycopg2-binary
pip install pillow
pip install openai
pip install requests
```

### 4. Configuration PostgreSQL

Créer une base de données :

```sql
CREATE DATABASE blog_db;
CREATE USER postgres WITH ENCRYPTED PASSWORD 'admin';
GRANT ALL PRIVILEGES ON DATABASE blog_db TO postgres;
```

### 5. Variables d'environnement

Créez un fichier `.env` :

```env
# Base de données
DB_NAME=blog_db
DB_USER=postgres
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=votre-clé-secrète-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI (optionnel)
OPENAI_API_KEY=votre-clé-openai
```

## ⚙️ Configuration

### Étapes de configuration

```bash
# 1. Migrations de base de données
python manage.py makemigrations
python manage.py migrate

# 2. Initialisation du système de rôles
python manage.py init_roles --create-admin

# 3. Compilation des traductions
python manage.py compilemessages

# 4. Collecte des fichiers statiques
python manage.py collectstatic
```

### Création d'un superutilisateur (optionnel)

```bash
python manage.py createsuperuser
```

## 🚀 Utilisation

### Démarrage du serveur

```bash
python manage.py runserver
```

🌐 **Application accessible à :** `http://localhost:8000`

### URLs principales

| Page | URL | Description |
|------|-----|-------------|
| 🏠 Accueil | `http://localhost:8000/` | Page d'accueil du blog |
| ⚙️ Administration | `http://localhost:8000/admin/` | Interface d'administration Django |
| 👥 Gestion utilisateurs | `http://localhost:8000/fr/gestion-utilisateurs/` | Gestion des rôles et utilisateurs |
| 🤖 ChatGPT | `http://localhost:8000/fr/chatgpt/` | Interface ChatGPT |
| 📊 Statistiques | `http://localhost:8000/fr/statistiques-roles/` | Statistiques des rôles |

### Compte par défaut

Après l'initialisation :
- **👤 Administrateur** : `admin` / `admin123`

## 👥 Système de rôles

### Hiérarchie des rôles

| Niveau | Rôle | Permissions |
|--------|------|-------------|
| 1️⃣ | **Lecteur** | Lecture des articles, commentaires, gestion profil |
| 2️⃣ | **Rédacteur** | + Création/édition de ses articles, accès ChatGPT |
| 3️⃣ | **Modérateur** | + Modération des commentaires, gestion signalements |
| 4️⃣ | **Éditeur** | + Édition de tous les articles, gestion catégories, statistiques |
| 5️⃣ | **Administrateur** | + Gestion complète des utilisateurs et système |

### Permissions détaillées

#### 👤 Lecteur (par défaut)
- ✅ Lecture des articles
- ✅ Ajout de commentaires
- ✅ Gestion de son profil

#### ✍️ Rédacteur
- ✅ Toutes les permissions du Lecteur
- ✅ Création et édition de ses propres articles
- ✅ Publication d'articles
- ✅ Accès au ChatGPT pour l'aide à la rédaction

#### 🛡️ Modérateur
- ✅ Toutes les permissions du Rédacteur
- ✅ Modération des commentaires
- ✅ Suppression de commentaires inappropriés
- ✅ Gestion des signalements

#### 📝 Éditeur
- ✅ Toutes les permissions du Modérateur
- ✅ Édition de tous les articles
- ✅ Gestion des catégories
- ✅ Accès aux statistiques
- ✅ Publication d'articles pour d'autres auteurs

#### 👑 Administrateur
- ✅ Toutes les permissions
- ✅ Gestion complète des utilisateurs
- ✅ Modification des rôles et statuts
- ✅ Accès à l'administration Django
- ✅ Gestion des paramètres système

## 🤖 API ChatGPT

### Configuration

1. **Obtenir une clé API OpenAI** sur [platform.openai.com](https://platform.openai.com)
2. **Ajouter la clé** dans `.env` :
   ```env
   OPENAI_API_KEY=sk-votre-clé-api-openai
   ```

### Fonctionnalités disponibles

#### 💬 Chat interactif
- Conversation en temps réel avec ChatGPT
- Suggestions d'articles automobiles
- Aide à la rédaction

#### 🎨 Génération d'images DALL-E
- Création d'images avec DALL-E
- Option activable pour chaque message
- Téléchargement des images générées

#### 📄 Génération d'articles complets
- Création automatique d'articles structurés
- Génération de titre, contenu et image
- Publication directe dans le blog

### Guide d'utilisation

1. **🔐 Connectez-vous** avec un compte ayant les permissions suffisantes
2. **🌐 Accédez à** `/fr/chatgpt/`
3. **⌨️ Tapez votre message** dans la zone de saisie
4. **🖼️ Activez l'option image** si souhaitée
5. **📤 Cliquez sur Envoyer**

## 🌍 Internationalisation

### Langues supportées

| Langue | Code | Statut | Flag |
|--------|------|--------|------|
| Français | `fr` | Par défaut | 🇫🇷 |
| Anglais | `en` | Supporté | 🇬🇧 |
| Espagnol | `es` | Supporté | 🇪🇸 |

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
- 🌐 Le sélecteur de langue dans l'interface
- 🔗 L'URL : `/fr/`, `/en/`, `/es/`
- ⚙️ Les paramètres de profil

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
├── 📄 manage.py                 # Point d'entrée Django
├── 📄 requirements.txt          # Dépendances Python
├── 🔐 .env                     # Variables d'environnement
├── 📄 .gitignore              # Fichiers ignorés par Git
├── 🔧 manage_translations.py   # Utilitaire de traductions
├── 🔧 compile_translations.py  # Compilation des traductions
├── 🗄️ db.sqlite3              # Base de données (si SQLite)
├── 📋 django.log              # Fichier de logs
│
├── 📁 mon_projet/             # Configuration principale
│   ├── ⚙️ settings.py         # Paramètres Django
│   ├── 🌐 urls.py            # URLs principales
│   ├── 🔧 wsgi.py            # Interface WSGI
│   └── 🔧 asgi.py            # Interface ASGI
│
├── 📁 blog/                   # Application principale
│   ├── ⚙️ admin.py           # Configuration admin Django
│   ├── 🏗️ models.py          # Modèles de données
│   ├── 👁️ views.py           # Vues principales
│   ├── 👥 views_roles.py     # Vues de gestion des rôles
│   ├── 🌐 urls.py            # URLs de l'application
│   ├── 📝 forms.py           # Formulaires Django
│   ├── 🎯 decorators.py      # Décorateurs personnalisés
│   ├── 🌍 language_middleware.py      # Middleware de langue
│   ├── 💡 recommendation_middleware.py # Middleware de recommandations
│   │
│   ├── 📁 management/        # Commandes de gestion
│   │   └── 📁 commands/
│   │       ├── 🔧 init_roles.py     # Initialisation des rôles
│   │       └── 👤 assign_role.py    # Attribution des rôles
│   │
│   ├── 📁 migrations/        # Migrations de base de données
│   ├── 📁 static/blog/       # Fichiers statiques (CSS, JS, images)
│   ├── 📁 templates/blog/    # Templates HTML
│   └── 📁 templatetags/      # Tags de template personnalisés
│
└── 📁 locale/                # Fichiers de traductions
    ├── 🇫🇷 fr/LC_MESSAGES/
    ├── 🇬🇧 en/LC_MESSAGES/
    └── 🇪🇸 es/LC_MESSAGES/
```

## 🔍 Dépannage

### ❌ Erreurs communes

#### 1. Erreur de base de données
```
django.db.utils.OperationalError: could not connect to server
```
**💡 Solution :** Vérifiez que PostgreSQL est démarré et les paramètres de connexion.

#### 2. Erreur de migrations
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```
**💡 Solution :**
```bash
python manage.py migrate --fake-initial
```

#### 3. Erreur de permissions
```
PermissionDenied: Vous n'avez pas les permissions nécessaires
```
**💡 Solution :**
```bash
python manage.py init_roles
```

#### 4. Erreur OpenAI
```
AuthenticationError: Incorrect API key provided
```
**💡 Solution :** Vérifiez la clé API OpenAI dans le fichier `.env`.

#### 5. Erreur de traductions
```
CommandError: Can't find msguniq
```
**💡 Solution :** Installez GNU gettext :
- **Windows** : [Télécharger gettext](https://mlocati.github.io/articles/gettext-iconv-windows.html)
- **Ubuntu/Debian** : `sudo apt-get install gettext`
- **macOS** : `brew install gettext`

### 🔧 Debugging

#### Consulter les logs
```bash
# Logs Django
tail -f django.log

# Logs du serveur de développement
python manage.py runserver --verbosity=2
```

#### Tests
```bash
# Lancer tous les tests
python manage.py test

# Tests spécifiques
python manage.py test blog.tests.TestModels
```

### 🔄 Réinitialisation complète

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

### 🚀 Développement

1. **🍴 Forkez** le projet
2. **🌿 Créez une branche** pour votre fonctionnalité
3. **💾 Commitez** vos changements
4. **🧪 Testez** votre code
5. **📤 Soumettez** une Pull Request

### 📋 Standards de code

- **📏 PEP 8** pour le style Python
- **💬 Commentaires** en français
- **🧪 Tests unitaires** pour toute nouvelle fonctionnalité
- **📚 Documentation** des nouvelles APIs

### 📝 Structure des commits

```
type(scope): description

[corps du message]

[footer]
```

**Exemples :**
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

1. **📖 Consultez** la section [Dépannage](#-dépannage)
2. **🔍 Vérifiez** les issues GitHub existantes
3. **📝 Ouvrez** une nouvelle issue si nécessaire

---

**📌 Version :** 1.0.0  
**📅 Dernière mise à jour :** Juin 2025

---

### 🎯 Quick Start

```bash
# Clone et setup rapide
git clone <votre-repo>
cd mon_projet
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py init_roles --create-admin
python manage.py runserver
```

🎉 **Votre blog automobile est prêt !** Rendez-vous sur `http://localhost:8000`