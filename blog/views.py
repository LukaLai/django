from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.utils import translation
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db import models
from django.views.decorators.http import require_POST
from .models import Article, Categorie, RecommandationEngine, ProfilUtilisateur, GestionnaireRoles
from .forms import ArticleForm, CommentaireForm, CategorieForm, RegistrationForm
from .decorators import role_required, permission_required_custom, admin_only, active_user_required
import base64
from django.core.exceptions import ValidationError
from django.http import HttpResponse
import logging
import os
import json
import requests

@login_required
def ajouter_article(request):
    logger = logging.getLogger(__name__)
    if request.method == 'POST':
        logger.info('Tentative d\'ajout d\'un article par %s', request.user)
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.auteur = request.user.get_full_name() or request.user.username
            try:
                image_file = request.FILES.get('image')
                if image_file:
                    image_file.seek(0)
                    article.image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
                    logger.info('Image encodée en base64 pour l\'article "%s"', article.titre)
            except Exception as e:
                logger.error('Erreur lors de l\'encodage de l\'image : %s', str(e))
                messages.error(request, f"Erreur lors de l'encodage de l'image: {str(e)}")
                return render(request, 'blog/ajouter_article.html', {'form': form})
            article.save()
            logger.info('Article "%s" ajouté par %s', article.titre, article.auteur)
            form.save_m2m()
            messages.success(request, 'Article ajouté avec succès!')
            return redirect('home')
        else:
            logger.warning('Formulaire d\'ajout d\'article invalide : %s', form.errors)
            messages.error(request, f"Erreur dans le formulaire : {form.errors}")
    else:
        logger.info('Affichage du formulaire d\'ajout d\'article pour %s', request.user)
        form = ArticleForm(initial={'auteur': request.user.get_full_name() or request.user.username})
    return render(request, 'blog/ajouter_article.html', {'form': form, 'LANGUAGE_CODE': request.LANGUAGE_CODE})

def ajouter_commentaire(request, article_id):
    logger = logging.getLogger(__name__)
    article = Article.objects.get(id=article_id)
    if request.method == 'POST':
        logger.info('Tentative d\'ajout d\'un commentaire sur l\'article "%s" par %s', article.titre, request.user)
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.article = article
            commentaire.save()
            logger.info('Commentaire ajouté sur "%s" par %s', article.titre, request.user)
            messages.success(request, 'Commentaire ajouté avec succès!')
            return redirect('home')
        else:
            logger.warning('Formulaire d\'ajout de commentaire invalide : %s', form.errors)
    else:
        logger.info('Affichage du formulaire d\'ajout de commentaire pour %s', request.user)
        form = CommentaireForm()
    return render(request, 'blog/ajouter_commentaire.html', {'form': form, 'article': article, 'LANGUAGE_CODE': request.LANGUAGE_CODE})

def ajouter_categorie(request):
    logger = logging.getLogger(__name__)
    if request.method == 'POST':
        logger.info('Tentative d\'ajout d\'une catégorie par %s', request.user)
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info('Catégorie ajoutée par %s', request.user)
            messages.success(request, 'Catégorie ajoutée avec succès!')
            return redirect('home')
        else:
            logger.warning('Formulaire d\'ajout de catégorie invalide : %s', form.errors)
    else:
        logger.info('Affichage du formulaire d\'ajout de catégorie pour %s', request.user)
        form = CategorieForm()
    return render(request, 'blog/ajouter_categorie.html', {'form': form, 'LANGUAGE_CODE': request.LANGUAGE_CODE})

def modifier_article(request, article_id):
    logger = logging.getLogger(__name__)
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        logger.info('Tentative de modification de l\'article "%s" par %s', article.titre, request.user)
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            logger.info('Article "%s" modifié par %s', article.titre, request.user)
            messages.success(request, 'Article modifié avec succès!')
            return redirect('home')
        else:
            logger.warning('Formulaire de modification d\'article invalide : %s', form.errors)
    else:
        logger.info('Affichage du formulaire de modification pour l\'article "%s" par %s', article.titre, request.user)
        form = ArticleForm(instance=article)
    return render(request, 'blog/modifier_article.html', {'form': form, 'article': article, 'LANGUAGE_CODE': request.LANGUAGE_CODE})

def deconnexion(request):
    logger = logging.getLogger(__name__)
    logger.info('Déconnexion de l\'utilisateur %s', request.user)
    logout(request)
    return redirect('home')

def liste_categories(request):
    logger = logging.getLogger(__name__)
    logger.info('Affichage de la liste des catégories pour %s', request.user)
    categories = Categorie.objects.all()
    return render(request, 'blog/liste_categories.html', {'categories': categories, 'LANGUAGE_CODE': request.LANGUAGE_CODE})

@login_required
def supprimer_categorie(request, categorie_id):
    logger = logging.getLogger(__name__)
    categorie = get_object_or_404(Categorie, id=categorie_id)
    if request.method == 'POST':
        logger.info('Suppression de la catégorie "%s" par %s', categorie.nom, request.user)
        categorie.delete()
        messages.success(request, 'Catégorie supprimée avec succès!')   
        return redirect('liste_categories')
    logger.info('Tentative d\'accès à la suppression de catégorie par %s', request.user)
    return redirect('liste_categories')

def profile(request):
    logger = logging.getLogger(__name__)
    logger.info('Affichage du profil pour %s', request.user)
    return render(request, 'blog/profile.html', {'LANGUAGE_CODE': request.LANGUAGE_CODE})

def home(request):
    logger = logging.getLogger(__name__)
    logger.info('Affichage de la page d\'accueil pour %s', request.user)
    
    # Obtenir des recommandations personnalisées
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    recommendations = RecommandationEngine.get_recommendations_for_user(
        user=user, 
        session_key=session_key, 
        limite=6
    )
    
    return render(request, 'blog/home.html', {
        'recommendations': recommendations,
    })

def articles(request):
    logger = logging.getLogger(__name__)
    logger.info('Affichage de la page des articles pour %s', request.user)
    articles = Article.objects.all()
    categories = Categorie.objects.all()
    categories_ids = request.GET.getlist('categories')
    if categories_ids:
        logger.info('Filtrage des articles par catégories : %s', categories_ids)
        articles = articles.filter(categories__id__in=categories_ids).distinct()
    selected_categories = categories_ids
    
    # Obtenir des recommandations personnalisées
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    recommendations = RecommandationEngine.get_recommendations_for_user(
        user=user, 
        session_key=session_key, 
        limite=6
    )
    
    return render(request, 'blog/articles.html', {
        'articles': articles,
        'categories': categories,
        'selected_categories': selected_categories,
        'recommendations': recommendations,
    })

def article_detail(request, article_id):
    logger = logging.getLogger(__name__)
    logger.info('Affichage de l\'article avec ID %s pour %s', article_id, request.user)
    article = get_object_or_404(Article, id=article_id)
    commentaires = article.commentaires.all()
    
    # Obtenir les articles similaires basés sur le contenu
    articles_similaires = article.get_articles_similaires(limite=4)
    
    # Obtenir des recommandations personnalisées
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    recommendations_personnalisees = RecommandationEngine.get_recommendations_for_user(
        user=user, 
        session_key=session_key, 
        limite=4
    )
    
    # Éviter que l'article actuel soit dans les recommandations
    recommendations_personnalisees = [art for art in recommendations_personnalisees if art.id != article.id]
    
    return render(request, 'blog/article_detail.html', {
        'article': article,
        'commentaires': commentaires,
        'articles_similaires': articles_similaires,
        'recommendations_personnalisees': recommendations_personnalisees,
        'LANGUAGE_CODE': request.LANGUAGE_CODE
    })

@login_required
def test_log_view(request):
    import logging
    import os
    logger = logging.getLogger(__name__)
    messages = []
    messages.append('INFO: Ceci est un message INFO depuis la vue')
    logger.info(messages[0])
    
    # Lecture des 50 dernières lignes du fichier de log
    log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'django.log')
    log_lines = []
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()[-50:]
        except UnicodeDecodeError:
            # Si l'encodage UTF-8 échoue, essayer avec latin-1 ou ignorer les erreurs
            try:
                with open(log_path, 'r', encoding='latin-1') as f:
                    log_lines = f.readlines()[-50:]
            except:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    log_lines = f.readlines()[-50:]
    return render(request, 'blog/test_log_affichage.html', {'messages': messages, 'log_lines': log_lines})

@login_required
def change_language(request):
    """Vue pour changer la langue de l'interface"""
    language = request.GET.get('language', settings.LANGUAGE_CODE)
    
    # Vérifier que la langue est supportée
    supported_languages = [lang[0] for lang in settings.LANGUAGES]
    if language in supported_languages:
        # Sauvegarder dans la session
        request.session['django_language'] = language
        # Activer la traduction
        translation.activate(language)
        
        messages.success(request, _('Langue changée avec succès'))
    else:
        messages.error(request, _('Langue non supportée'))
    
    # Rediriger vers la page précédente ou l'accueil
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# ===== VUES DE GESTION DES UTILISATEURS ET RÔLES =====

@role_required('administrateur')
def gestion_utilisateurs(request):
    """Vue pour la gestion des utilisateurs (administrateurs seulement)"""
    logger = logging.getLogger(__name__)
    logger.info('Accès à la gestion des utilisateurs par %s', request.user)
    
    # Filtres
    role_filter = request.GET.get('role', '')
    statut_filter = request.GET.get('statut', '')
    search_query = request.GET.get('search', '')    # Requête de base - Articles et commentaires basés sur le nom d'utilisateur
    utilisateurs = User.objects.select_related('profil')
    
    # Appliquer les filtres
    if role_filter:
        utilisateurs = utilisateurs.filter(profil__role=role_filter)
    
    if statut_filter:
        utilisateurs = utilisateurs.filter(profil__statut=statut_filter)
    
    if search_query:
        utilisateurs = utilisateurs.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
      # Pagination
    paginator = Paginator(utilisateurs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Ajouter les statistiques pour chaque utilisateur dans la page
    for utilisateur in page_obj:
        utilisateur.nb_articles = Article.objects.filter(auteur=utilisateur.username).count()
        utilisateur.nb_commentaires = 0  # Sera calculé selon la structure du modèle Commentaire
    
    # Statistiques
    stats = {
        'total_utilisateurs': User.objects.count(),
        'utilisateurs_actifs': ProfilUtilisateur.objects.filter(statut='actif').count(),
        'redacteurs': ProfilUtilisateur.objects.filter(role='redacteur').count(),
        'moderateurs': ProfilUtilisateur.objects.filter(role='moderateur').count(),
        'editeurs': ProfilUtilisateur.objects.filter(role='editeur').count(),
        'administrateurs': ProfilUtilisateur.objects.filter(role='administrateur').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'roles_choices': ProfilUtilisateur.ROLES_CHOICES,
        'statuts_choices': ProfilUtilisateur.STATUTS_CHOICES,
        'current_filters': {
            'role': role_filter,
            'statut': statut_filter,
            'search': search_query,
        },
        'stats': stats,
        'LANGUAGE_CODE': request.LANGUAGE_CODE,
    }
    
    return render(request, 'blog/gestion_utilisateurs.html', context)


@admin_only
@require_POST
def modifier_role_utilisateur(request):
    """Modifier le rôle d'un utilisateur via AJAX"""
    logger = logging.getLogger(__name__)
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        nouveau_role = data.get('nouveau_role')
        
        logger.info('Tentative de modification du rôle de l\'utilisateur %s vers %s par %s', user_id, nouveau_role, request.user)
        
        # Vérifications
        if not user_id or not nouveau_role:
            return JsonResponse({'success': False, 'message': 'Données manquantes'})
        
        roles_valides = [r[0] for r in ProfilUtilisateur.ROLES_CHOICES]
        if nouveau_role not in roles_valides:
            return JsonResponse({'success': False, 'message': 'Rôle invalide'})
        
        # Récupérer l'utilisateur
        user = get_object_or_404(User, id=user_id)
        
        # Empêcher de modifier son propre rôle
        if user == request.user:
            return JsonResponse({'success': False, 'message': 'Vous ne pouvez pas modifier votre propre rôle'})
        
        # Assigner le nouveau rôle
        GestionnaireRoles.assigner_role_utilisateur(user, nouveau_role)
        
        logger.info('Rôle de %s modifié vers %s par %s', user.username, nouveau_role, request.user)
        
        return JsonResponse({
            'success': True, 
            'message': f'Rôle modifié avec succès pour {user.username}'
        })
        
    except Exception as e:
        logger.error('Erreur lors de la modification du rôle : %s', str(e))
        return JsonResponse({'success': False, 'message': str(e)})


@admin_only
@require_POST
def modifier_statut_utilisateur(request):
    """Modifier le statut d'un utilisateur via AJAX"""
    logger = logging.getLogger(__name__)
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        nouveau_statut = data.get('nouveau_statut')
        
        logger.info('Tentative de modification du statut de l\'utilisateur %s vers %s par %s', user_id, nouveau_statut, request.user)
        
        # Vérifications
        if not user_id or not nouveau_statut:
            return JsonResponse({'success': False, 'message': 'Données manquantes'})
        
        statuts_valides = [s[0] for s in ProfilUtilisateur.STATUTS_CHOICES]
        if nouveau_statut not in statuts_valides:
            return JsonResponse({'success': False, 'message': 'Statut invalide'})
        
        # Récupérer l'utilisateur
        user = get_object_or_404(User, id=user_id)
        
        # Empêcher de modifier son propre statut
        if user == request.user:
            return JsonResponse({'success': False, 'message': 'Vous ne pouvez pas modifier votre propre statut'})
        
        # Modifier le statut
        if hasattr(user, 'profil'):
            user.profil.statut = nouveau_statut
            user.profil.save()
            
            logger.info('Statut de %s modifié vers %s par %s', user.username, nouveau_statut, request.user)
            
            return JsonResponse({
                'success': True, 
                'message': f'Statut modifié avec succès pour {user.username}'
            })
        else:
            return JsonResponse({'success': False, 'message': 'Profil utilisateur non trouvé'})
        
    except Exception as e:
        logger.error('Erreur lors de la modification du statut : %s', str(e))
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def mon_profil(request):
    """Vue pour que l'utilisateur gère son propre profil"""
    logger = logging.getLogger(__name__)
    profil = request.user.profil
    
    if request.method == 'POST':
        logger.info('Tentative de mise à jour du profil par %s', request.user)
        
        # Mise à jour des informations du profil
        profil.bio = request.POST.get('bio', '')
        profil.notifications_email = 'notifications_email' in request.POST
        profil.notifications_nouveaux_articles = 'notifications_nouveaux_articles' in request.POST
        profil.notifications_commentaires = 'notifications_commentaires' in request.POST
        
        # Mise à jour des informations utilisateur
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        
        profil.save()
        request.user.save()
        
        logger.info('Profil de %s mis à jour avec succès', request.user)
        messages.success(request, 'Profil mis à jour avec succès!')
        return redirect('mon_profil')
    
    # Statistiques de l'utilisateur
    stats = {
        'nb_articles': Article.objects.filter(auteur=request.user.username).count(),
        'nb_commentaires': 0,  # Sera calculé quand le modèle Commentaire aura un utilisateur
        'articles_recents': Article.objects.filter(auteur=request.user.username).order_by('-date_creation')[:5],
    }
    
    context = {
        'profil': profil,
        'stats': stats,
        'LANGUAGE_CODE': request.LANGUAGE_CODE,
    }
    
    return render(request, 'blog/mon_profil.html', context)


@permission_required_custom('can_view_statistics')
def statistiques_roles(request):
    """Vue pour afficher les statistiques des rôles et permissions"""
    logger = logging.getLogger(__name__)
    logger.info('Accès aux statistiques des rôles par %s', request.user)
    
    # Statistiques générales
    stats_generales = {
        'total_utilisateurs': User.objects.count(),
        'utilisateurs_actifs': ProfilUtilisateur.objects.filter(statut='actif').count(),
        'articles_total': Article.objects.count(),
        'commentaires_total': 0,  # Sera calculé quand nécessaire
    }
    
    # Répartition par rôle
    stats_roles = {}
    for role, description in ProfilUtilisateur.ROLES_CHOICES:
        count = ProfilUtilisateur.objects.filter(role=role).count()
        stats_roles[description] = count
    
    # Répartition par statut
    stats_statuts = {}
    for statut, description in ProfilUtilisateur.STATUTS_CHOICES:
        count = ProfilUtilisateur.objects.filter(statut=statut).count()
        stats_statuts[description] = count
      # Articles par auteur (top 10)
    # Créer un dictionnaire des auteurs avec leurs statistiques  
    auteurs_stats = {}
    
    # Compter les articles par nom d'utilisateur
    for article in Article.objects.all():
        if article.auteur not in auteurs_stats:
            auteurs_stats[article.auteur] = {'nb_articles': 0, 'utilisateur': None}
        auteurs_stats[article.auteur]['nb_articles'] += 1
    
    # Associer les profils utilisateurs
    for username, stats in auteurs_stats.items():
        try:
            user = User.objects.get(username=username)
            if hasattr(user, 'profil'):
                stats['profil'] = user.profil
                stats['utilisateur'] = user
        except User.DoesNotExist:
            continue
    
    # Filtrer et trier pour obtenir le top 10
    top_auteurs = [
        {
            'utilisateur': stats['utilisateur'],
            'nb_articles': stats['nb_articles'],
            'get_role_display': stats['profil'].get_role_display() if stats.get('profil') else 'Inconnu'
        }
        for stats in auteurs_stats.values()
        if stats['utilisateur'] and stats.get('profil')
    ]
    top_auteurs = sorted(top_auteurs, key=lambda x: x['nb_articles'], reverse=True)[:10]
    
    context = {
        'stats_generales': stats_generales,
        'stats_roles': stats_roles,
        'stats_statuts': stats_statuts,
        'top_auteurs': top_auteurs,
        'LANGUAGE_CODE': request.LANGUAGE_CODE,
    }
    
    return render(request, 'blog/statistiques_roles.html', context)


@role_required('administrateur')
def voir_profil_utilisateur(request, user_id):
    """Vue pour voir le profil détaillé d'un utilisateur (admin seulement)"""
    logger = logging.getLogger(__name__)
    utilisateur = get_object_or_404(User, id=user_id)
    profil = utilisateur.profil
    
    logger.info('Consultation du profil de %s par %s', utilisateur.username, request.user)
    
    # Statistiques de l'utilisateur
    stats = {
        'nb_articles': Article.objects.filter(auteur=utilisateur.username).count(),
        'nb_commentaires': 0,  # Sera calculé plus tard
        'articles_recents': Article.objects.filter(auteur=utilisateur.username).order_by('-date_creation')[:10],
        'date_derniere_connexion': profil.derniere_connexion,
    }
    
    context = {
        'utilisateur_profil': utilisateur,
        'profil': profil,
        'stats': stats,
        'LANGUAGE_CODE': request.LANGUAGE_CODE,
    }
    
    return render(request, 'blog/voir_profil_utilisateur.html', context)

def register(request):
    """Vue pour l'inscription des nouveaux utilisateurs"""
    logger = logging.getLogger(__name__)
    
    if request.user.is_authenticated:
        logger.info('Utilisateur déjà connecté %s tente d\'accéder à l\'inscription', request.user)
        messages.info(request, 'Vous êtes déjà connecté.')
        return redirect('home')
    
    if request.method == 'POST':
        logger.info('Tentative d\'inscription d\'un nouvel utilisateur')
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Créer l'utilisateur
                user = form.save()
                username = form.cleaned_data.get('username')
                logger.info('Nouvel utilisateur créé : %s', username)
                
                # Connecter automatiquement l'utilisateur après inscription
                user = authenticate(
                    username=user.username,
                    password=form.cleaned_data.get('password1')
                )
                if user is not None:
                    login(request, user)
                    logger.info('Utilisateur %s connecté automatiquement après inscription', username)
                    messages.success(request, f'Bienvenue {username} ! Votre compte a été créé avec succès.')
                    return redirect('home')
                else:
                    logger.warning('Échec de la connexion automatique pour %s', username)
                    messages.success(request, f'Compte créé avec succès pour {username}. Vous pouvez maintenant vous connecter.')
                    return redirect('login')
                    
            except Exception as e:
                logger.error('Erreur lors de la création du compte : %s', str(e))
                messages.error(request, f'Erreur lors de la création du compte : {str(e)}')
        else:
            logger.warning('Formulaire d\'inscription invalide : %s', form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        logger.info('Affichage du formulaire d\'inscription')
        form = RegistrationForm()
    
    return render(request, 'blog/register.html', {
        'form': form,
        'LANGUAGE_CODE': request.LANGUAGE_CODE
    })

# ===== VUES CHATGPT =====

@login_required
def chatgpt_view(request):
    """Vue pour afficher la page de chat ChatGPT"""
    return render(request, 'blog/chatgpt.html', {
        'LANGUAGE_CODE': request.LANGUAGE_CODE
    })

@login_required
@require_POST
def generate_article_ai(request):
    """API pour générer un article complet avec ChatGPT"""
    logger = logging.getLogger(__name__)
    
    try:
        # Récupérer les données JSON
        data = json.loads(request.body)
        user_prompt = data.get('prompt', '').strip()
        
        if not user_prompt:
            return JsonResponse({
                'success': False,
                'error': 'Prompt vide'
            })
        
        logger.info('Génération d\'article IA pour %s: %s', 
                   request.user.username, user_prompt[:100])
        
        # Configuration de l'API OpenAI
        api_key = ''
        
        # Headers pour l'API
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Prompt optimisé pour la génération d'articles
        system_prompt = """Tu es un assistant expert en création de contenu. Ta tâche est de générer un article de blog complet et bien structuré.

CONSIGNES IMPORTANTES:
1. Génère un titre accrocheur et informatif
2. Écris un contenu détaillé, bien structuré avec des paragraphes
3. Utilise un ton professionnel mais accessible
4. Inclus des exemples pratiques quand c'est pertinent
5. Assure-toi que l'article fait au moins 500 mots
6. Structure ton contenu avec des sous-titres si nécessaire
7. Conclus avec un résumé ou une ouverture

Format de réponse attendu:
TITRE: [Le titre de l'article]
CONTENU: [Le contenu complet de l'article]
CATEGORIES: [Liste de 1-3 catégories suggérées séparées par des virgules]

Exemple de catégories possibles: Développement Web, Django, JavaScript, CSS, Python, Programmation, Technologie, Design, Base de données, etc."""
        
        # Appel à l'API ChatGPT
        chat_url = 'https://api.openai.com/v1/chat/completions'
        chat_payload = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': f"Génère un article de blog sur le sujet suivant: {user_prompt}"
                }
            ],
            'max_tokens': 2000,
            'temperature': 0.7
        }
        
        chat_response = requests.post(chat_url, headers=headers, json=chat_payload, timeout=60)
        
        if chat_response.status_code != 200:
            logger.error('Erreur API ChatGPT (%d): %s', chat_response.status_code, chat_response.text)
            return JsonResponse({
                'success': False,
                'error': f'Erreur de l\'API ChatGPT: {chat_response.status_code}'
            })
        
        chat_data = chat_response.json()
        ai_response = chat_data['choices'][0]['message']['content']
        
        # Parser la réponse pour extraire titre, contenu et catégories
        try:
            titre = ""
            contenu = ""
            categories_suggestions = []
            
            lines = ai_response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('TITRE:'):
                    titre = line.replace('TITRE:', '').strip()
                    current_section = 'titre'
                elif line.startswith('CONTENU:'):
                    contenu = line.replace('CONTENU:', '').strip()
                    current_section = 'contenu'
                elif line.startswith('CATEGORIES:'):
                    categories_text = line.replace('CATEGORIES:', '').strip()
                    categories_suggestions = [cat.strip() for cat in categories_text.split(',') if cat.strip()]
                    current_section = 'categories'
                elif current_section == 'contenu' and line:
                    contenu += '\n' + line
            
            # Si le format n'est pas respecté, essayer de deviner
            if not titre or not contenu:
                # Prendre la première ligne comme titre potentiel
                response_lines = [line.strip() for line in ai_response.split('\n') if line.strip()]
                if response_lines:
                    titre = response_lines[0] if not titre else titre
                    contenu = '\n'.join(response_lines[1:]) if not contenu else contenu
            
            # Nettoyer le titre
            titre = titre.replace('TITRE:', '').replace('#', '').strip()
              # Mapper les catégories suggérées aux catégories existantes
            categories_ids = []
            if categories_suggestions:
                # Récupérer toutes les catégories existantes
                categories_existantes = Categorie.objects.all()
                
                for suggestion in categories_suggestions:
                    # Chercher une catégorie correspondante (insensible à la casse)
                    categorie_correspondante = categories_existantes.filter(
                        nom__icontains=suggestion
                    ).first()
                    
                    if not categorie_correspondante:
                        # Chercher par correspondance partielle
                        for cat in categories_existantes:
                            if suggestion.lower() in cat.nom.lower() or cat.nom.lower() in suggestion.lower():
                                categorie_correspondante = cat
                                break
                    
                    if categorie_correspondante:
                        categories_ids.append(categorie_correspondante.id)
                
                # Si aucune catégorie trouvée, prendre les premières catégories par défaut
                if not categories_ids and categories_existantes.exists():
                    categories_ids = [categories_existantes.first().id]
            
            result = {
                'success': True,
                'titre': titre,
                'contenu': contenu,
                'categories': categories_ids
            }
            
            # Générer une image avec DALL-E si le titre et contenu sont disponibles
            try:
                # Créer un prompt pour l'image basé sur le titre de l'article
                image_prompt = f"Create a professional, modern illustration for a blog article titled '{titre}'. The image should be visually appealing, relevant to the topic, and suitable for a professional blog. Style: clean, modern, professional."
                
                # Limiter la longueur du prompt pour DALL-E
                if len(image_prompt) > 1000:
                    image_prompt = f"Professional illustration for article: {titre[:100]}..."
                
                # Appel à l'API DALL-E
                dalle_url = 'https://api.openai.com/v1/images/generations'
                dalle_payload = {
                    'model': 'dall-e-3',
                    'prompt': image_prompt,
                    'n': 1,
                    'quality': 'standard',
                    'size': '1024x1024'
                }
                
                logger.info('Génération d\'image DALL-E pour l\'article: %s', titre[:50])
                dalle_response = requests.post(dalle_url, headers=headers, json=dalle_payload, timeout=60)
                
                if dalle_response.status_code == 200:
                    dalle_data = dalle_response.json()
                    if 'data' in dalle_data and len(dalle_data['data']) > 0:
                        image_url = dalle_data['data'][0]['url']
                        result['image_url'] = image_url
                        logger.info('Image DALL-E générée avec succès pour l\'article: %s', titre[:50])
                    else:
                        logger.warning('Réponse DALL-E vide pour l\'article: %s', titre[:50])
                else:
                    logger.warning('Erreur DALL-E (%d) pour l\'article: %s - %s', 
                                 dalle_response.status_code, titre[:50], dalle_response.text)
                    
            except Exception as e:
                logger.warning('Erreur lors de la génération d\'image DALL-E: %s', str(e))
                # L'erreur d'image ne doit pas empêcher le succès de l'article
            
            logger.info('Article généré avec succès pour %s: %s', 
                       request.user.username, titre[:50])
            
            return JsonResponse(result)
            
        except Exception as e:
            logger.error('Erreur lors du parsing de la réponse IA: %s', str(e))
            # En cas d'erreur de parsing, utiliser la réponse brute
            return JsonResponse({
                'success': True,
                'titre': 'Article généré par IA',
                'contenu': ai_response,
                'categories': []
            })
            
    except json.JSONDecodeError:
        logger.error('Erreur de décodage JSON dans generate_article_ai')
        return JsonResponse({
            'success': False,
            'error': 'Format de données invalide'
        })
    except requests.exceptions.Timeout:
        logger.error('Timeout lors de la génération d\'article IA')
        return JsonResponse({
            'success': False,
            'error': 'Délai d\'attente dépassé. Veuillez réessayer.'
        })
    except requests.exceptions.RequestException as e:
        logger.error('Erreur de requête OpenAI pour génération d\'article: %s', str(e))
        return JsonResponse({
            'success': False,
            'error': 'Erreur de connexion à l\'API. Veuillez réessayer.'
        })
    except Exception as e:
        logger.error('Erreur inattendue dans generate_article_ai: %s', str(e))
        return JsonResponse({
            'success': False,
            'error': 'Une erreur inattendue s\'est produite.'
        })

@login_required
@require_POST
def chatgpt_api(request):
    """API pour communiquer avec ChatGPT et DALL-E"""
    logger = logging.getLogger(__name__)
    
    try:
        # Récupérer les données JSON
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        generate_image = data.get('generate_image', False)
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Message vide'
            })
        
        logger.info('Requête ChatGPT de %s: %s (Image: %s)', 
                   request.user.username, user_message[:100], generate_image)
        
        # Configuration de l'API OpenAI
        api_key = ''
        
        # Headers pour l'API
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Appel à l'API ChatGPT pour la réponse textuelle
        chat_url = 'https://api.openai.com/v1/chat/completions'
        chat_payload = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'system',
                    'content': 'Tu es un assistant intelligent et serviable. Réponds de manière claire, précise et utile. Si la question concerne la programmation, le développement web ou Django, donne des exemples pratiques quand c\'est pertinent.'
                },
                {
                    'role': 'user',
                    'content': user_message
                }
            ],
            'max_tokens': 1000,
            'temperature': 0.7
        }
        
        # Obtenir la réponse textuelle de ChatGPT
        chat_response = requests.post(chat_url, headers=headers, json=chat_payload, timeout=30)
        
        if chat_response.status_code != 200:
            logger.error('Erreur API ChatGPT (%d): %s', chat_response.status_code, chat_response.text)
            return JsonResponse({
                'success': False,
                'error': f'Erreur de l\'API ChatGPT: {chat_response.status_code}'
            })
        
        chat_data = chat_response.json()
        ai_response = chat_data['choices'][0]['message']['content']
        
        result = {
            'success': True,
            'response': ai_response
        }
        
        # Si génération d'image demandée, appeler DALL-E
        if generate_image:
            try:
                # Créer un prompt optimisé pour DALL-E basé sur le message utilisateur
                if any(keyword in user_message.lower() for keyword in ['dessine', 'créé', 'génère', 'image', 'photo', 'illustration']):
                    # Le message contient déjà une demande d'image
                    image_prompt = user_message
                else:
                    # Créer un prompt d'image basé sur le contexte du message
                    image_prompt = f"Une illustration créative et artistique représentant: {user_message}"
                
                # Limiter la taille du prompt DALL-E à 1000 caractères
                if len(image_prompt) > 1000:
                    image_prompt = image_prompt[:997] + "..."
                
                dalle_url = 'https://api.openai.com/v1/images/generations'
                dalle_payload = {
                    'model': 'dall-e-3',
                    'prompt': image_prompt,
                    'n': 1,
                    'size': '1024x1024',
                    'quality': 'standard',
                    'response_format': 'url'
                }
                
                logger.info('Génération d\'image DALL-E pour %s avec prompt: %s', 
                           request.user.username, image_prompt[:100])
                
                dalle_response = requests.post(dalle_url, headers=headers, json=dalle_payload, timeout=60)
                
                if dalle_response.status_code == 200:
                    dalle_data = dalle_response.json()
                    image_url = dalle_data['data'][0]['url']
                    
                    result['image_url'] = image_url
                    result['response'] += f"\n\n🎨 J'ai également généré une image basée sur votre demande !"
                    
                    logger.info('Image DALL-E générée avec succès pour %s', request.user.username)
                else:
                    logger.error('Erreur API DALL-E (%d): %s', dalle_response.status_code, dalle_response.text)
                    result['response'] += f"\n\n⚠️ Désolé, je n'ai pas pu générer l'image demandée. Erreur DALL-E: {dalle_response.status_code}"
                    
            except Exception as e:
                logger.error('Erreur lors de la génération d\'image: %s', str(e))
                result['response'] += f"\n\n⚠️ Désolé, une erreur s'est produite lors de la génération de l'image."
        
        logger.info('Réponse complète envoyée pour %s', request.user.username)
        return JsonResponse(result)
            
    except json.JSONDecodeError:
        logger.error('Erreur de décodage JSON dans chatgpt_api')
        return JsonResponse({
            'success': False,
            'error': 'Format de données invalide'
        })
    except requests.exceptions.Timeout:
        logger.error('Timeout lors de l\'appel à l\'API OpenAI')
        return JsonResponse({
            'success': False,
            'error': 'Délai d\'attente dépassé. Veuillez réessayer.'
        })
    except requests.exceptions.RequestException as e:
        logger.error('Erreur de requête vers OpenAI: %s', str(e))
        return JsonResponse({
            'success': False,
            'error': 'Erreur de connexion à l\'API. Veuillez réessayer.'
        })
    except Exception as e:
        logger.error('Erreur inattendue dans chatgpt_api: %s', str(e))
        return JsonResponse({
            'success': False,
            'error': 'Une erreur inattendue s\'est produite.'
        })
