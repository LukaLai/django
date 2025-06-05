"""
Vues pour la gestion des utilisateurs et des rôles
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from .decorators import role_required, permission_required_custom, admin_only
from .models import ProfilUtilisateur, GestionnaireRoles, Article, Commentaire


@role_required('administrateur')
def gestion_utilisateurs(request):
    """Vue pour la gestion des utilisateurs (administrateurs seulement)"""
    # Filtres
    role_filter = request.GET.get('role', '')
    statut_filter = request.GET.get('statut', '')
    search_query = request.GET.get('search', '')
      # Requête de base - Articles et commentaires basés sur le nom d'utilisateur
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
        utilisateur.nb_commentaires = Commentaire.objects.filter(auteur=utilisateur.username).count()
    
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
    }
    
    return render(request, 'blog/gestion_utilisateurs.html', context)


@admin_only
@require_POST
def modifier_role_utilisateur(request):
    """Modifier le rôle d'un utilisateur via AJAX"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        nouveau_role = data.get('nouveau_role')
        
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
        
        return JsonResponse({
            'success': True, 
            'message': f'Rôle modifié avec succès pour {user.username}'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@admin_only
@require_POST
def modifier_statut_utilisateur(request):
    """Modifier le statut d'un utilisateur via AJAX"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        nouveau_statut = data.get('nouveau_statut')
        
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
            
            return JsonResponse({
                'success': True, 
                'message': f'Statut modifié avec succès pour {user.username}'
            })
        else:
            return JsonResponse({'success': False, 'message': 'Profil utilisateur non trouvé'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def mon_profil(request):
    """Vue pour que l'utilisateur gère son propre profil"""
    profil = request.user.profil
    
    if request.method == 'POST':
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
        
        messages.success(request, 'Profil mis à jour avec succès!')
        return redirect('mon_profil')
    
    # Statistiques de l'utilisateur
    stats = {
        'nb_articles': Article.objects.filter(auteur=request.user.username).count(),
        'nb_commentaires': Commentaire.objects.filter(auteur=request.user.username).count(),
        'articles_recents': Article.objects.filter(auteur=request.user.username).order_by('-date_creation')[:5],
    }
    
    context = {
        'profil': profil,
        'stats': stats,
    }
    
    return render(request, 'blog/mon_profil.html', context)


@permission_required_custom('can_view_statistics')
def statistiques_roles(request):
    """Vue pour afficher les statistiques des rôles et permissions"""
    # Statistiques générales
    stats_generales = {
        'total_utilisateurs': User.objects.count(),
        'utilisateurs_actifs': ProfilUtilisateur.objects.filter(statut='actif').count(),
        'articles_total': Article.objects.count(),
        'commentaires_total': Commentaire.objects.count(),
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
    }
    
    return render(request, 'blog/statistiques_roles.html', context)
