# 🚀 Guide de démarrage rapide

Ce guide vous permettra de lancer l'application en moins de 10 minutes.

## Prérequis rapides

- Python 3.8+ installé
- PostgreSQL installé et démarré
- Git installé

## Installation express

### 1. Clone et setup
```bash
git clone <repository-url>
cd mon_projet
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 2. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 3. Configuration de la base de données

Dans PostgreSQL :
```sql
CREATE DATABASE blog_db;
CREATE USER postgres WITH ENCRYPTED PASSWORD 'admin';
GRANT ALL PRIVILEGES ON DATABASE blog_db TO postgres;
```

### 4. Configuration de l'environnement
```bash
# Copiez le fichier d'exemple
cp .env.example .env

# Éditez .env avec vos paramètres
# La configuration par défaut devrait fonctionner
```

### 5. Initialisation de l'application
```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Système de rôles et admin
python manage.py init_roles --create-admin

# Traductions
python manage.py compilemessages
```

### 6. Lancement
```bash
python manage.py runserver
```

## 🎉 C'est parti !

- **Application** : http://localhost:8000
- **Admin** : http://localhost:8000/admin
- **Compte admin** : admin / admin123

## Prochaines étapes

1. **Explorez l'interface** : Créez des articles, testez les rôles
2. **Configurez ChatGPT** : Ajoutez votre clé OpenAI dans `.env`
3. **Personnalisez** : Modifiez les templates et styles selon vos besoins

## Problèmes fréquents

### ❌ Erreur de connexion PostgreSQL
```bash
# Vérifiez que PostgreSQL est démarré
sudo service postgresql start  # Linux
brew services start postgresql # macOS
```

### ❌ Erreur de migrations
```bash
python manage.py migrate --fake-initial
```

### ❌ Erreur de permissions
```bash
python manage.py init_roles
```

## 📖 Documentation complète

Pour plus de détails, consultez le [README.md](README.md) complet.
