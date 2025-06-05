"""
Décorateurs pour gérer les permissions et rôles dans le blog
"""

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def role_required(*roles):
    """
    Décorateur pour vérifier si l'utilisateur a un des rôles requis
    
    Usage:
    @role_required('redacteur', 'editeur', 'administrateur')
    def ma_vue(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'profil'):
                messages.error(request, "Profil utilisateur non trouvé.")
                return redirect('home')
            
            if request.user.profil.statut != 'actif':
                messages.error(request, "Votre compte n'est pas actif.")
                return redirect('home')
            
            if request.user.profil.role in roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
                return redirect('home')
        
        return wrapper
    return decorator


def permission_required_custom(permission_name, raise_exception=False):
    """
    Décorateur pour vérifier une permission spécifique
    
    Usage:
    @permission_required_custom('can_publish_articles')
    def ma_vue(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'profil'):
                if raise_exception:
                    raise PermissionDenied("Profil utilisateur non trouvé")
                messages.error(request, "Profil utilisateur non trouvé.")
                return redirect('home')
            
            if request.user.profil.statut != 'actif':
                if raise_exception:
                    raise PermissionDenied("Compte utilisateur non actif")
                messages.error(request, "Votre compte n'est pas actif.")
                return redirect('home')
            
            # Vérifier la permission via les méthodes du profil
            permission_methods = {
                'can_publish_articles': 'peut_publier_articles',
                'can_moderate_comments': 'peut_moderer_commentaires',
                'can_manage_categories': 'peut_gerer_categories',
                'can_manage_users': 'peut_gerer_utilisateurs',
                'can_view_statistics': 'peut_voir_statistiques',
            }
            
            method_name = permission_methods.get(permission_name)
            if method_name and hasattr(request.user.profil, method_name):
                has_permission = getattr(request.user.profil, method_name)()
                if has_permission:
                    return view_func(request, *args, **kwargs)
            
            # Vérifier aussi les permissions Django
            if request.user.has_perm(f'blog.{permission_name}'):
                return view_func(request, *args, **kwargs)
            
            if raise_exception:
                raise PermissionDenied("Permission insuffisante")
            
            messages.error(request, "Vous n'avez pas les permissions nécessaires.")
            return redirect('home')
        
        return wrapper
    return decorator


def author_or_role_required(*roles):
    """
    Décorateur pour vérifier si l'utilisateur est l'auteur de l'objet ou a un des rôles requis
    
    Usage:
    @author_or_role_required('editeur', 'administrateur')
    def modifier_article(request, article_id):
        article = get_object_or_404(Article, id=article_id)
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'profil'):
                messages.error(request, "Profil utilisateur non trouvé.")
                return redirect('home')
            
            if request.user.profil.statut != 'actif':
                messages.error(request, "Votre compte n'est pas actif.")
                return redirect('home')
            
            # Vérifier si l'utilisateur a un des rôles requis
            if request.user.profil.role in roles:
                return view_func(request, *args, **kwargs)
            
            # Si pas le bon rôle, la vue doit vérifier si c'est l'auteur
            # Cette vérification se fait dans la vue elle-même
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def active_user_required(view_func):
    """
    Décorateur pour s'assurer que l'utilisateur est actif
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profil'):
            messages.error(request, "Profil utilisateur non trouvé.")
            return redirect('home')
        
        if request.user.profil.statut != 'actif':
            messages.error(request, "Votre compte n'est pas actif.")
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def admin_only(view_func):
    """
    Décorateur pour restricter l'accès aux administrateurs uniquement
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profil'):
            return HttpResponseForbidden("Accès refusé : profil non trouvé")
        
        if request.user.profil.role != 'administrateur' or request.user.profil.statut != 'actif':
            return HttpResponseForbidden("Accès refusé : permissions insuffisantes")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


class RoleRequiredMixin:
    """
    Mixin pour les vues basées sur les classes pour vérifier les rôles
    """
    required_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not hasattr(request.user, 'profil'):
            messages.error(request, "Profil utilisateur non trouvé.")
            return redirect('home')
        
        if request.user.profil.statut != 'actif':
            messages.error(request, "Votre compte n'est pas actif.")
            return redirect('home')
        
        if self.required_roles and request.user.profil.role not in self.required_roles:
            messages.error(request, "Vous n'avez pas les permissions nécessaires.")
            return redirect('home')
        
        return super().dispatch(request, *args, **kwargs)
