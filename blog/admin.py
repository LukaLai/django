from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Article, Categorie, Commentaire, InteractionUtilisateur, ProfilUtilisateur

# Configuration de l'admin pour les Catégories
@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'icone', 'couleur')
    list_filter = ('couleur',)
    search_fields = ('nom', 'description')
    ordering = ('nom',)

# Configuration de l'admin pour les Articles
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'date_creation', 'vues', 'get_categories')
    list_filter = ('date_creation', 'auteur', 'categories')
    search_fields = ('titre', 'contenu', 'auteur')
    filter_horizontal = ('categories',)  # Interface améliorée pour les relations many-to-many
    date_hierarchy = 'date_creation'
    ordering = ('-date_creation',)
    readonly_fields = ('vues', 'date_creation')
    
    def get_categories(self, obj):
        return ", ".join([cat.nom for cat in obj.categories.all()])
    get_categories.short_description = 'Catégories'

# Configuration de l'admin pour les Commentaires
@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('article', 'auteur', 'date_creation', 'get_contenu_preview')
    list_filter = ('date_creation', 'article')
    search_fields = ('auteur', 'contenu', 'article__titre')
    date_hierarchy = 'date_creation'
    ordering = ('-date_creation',)
    readonly_fields = ('date_creation',)
    
    def get_contenu_preview(self, obj):
        return obj.contenu[:50] + "..." if len(obj.contenu) > 50 else obj.contenu
    get_contenu_preview.short_description = 'Aperçu du contenu'

# Configuration de l'admin pour les Interactions Utilisateur
@admin.register(InteractionUtilisateur)
class InteractionUtilisateurAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'article', 'type_interaction', 'date_interaction', 'temps_lecture')
    list_filter = ('date_interaction', 'type_interaction', 'article')
    search_fields = ('utilisateur__username', 'article__titre')
    date_hierarchy = 'date_interaction'
    ordering = ('-date_interaction',)
    readonly_fields = ('date_interaction',)

# Configuration de l'admin pour les Profils Utilisateurs
@admin.register(ProfilUtilisateur)
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'role', 'statut', 'date_inscription', 'derniere_connexion', 'nombre_articles', 'nombre_commentaires')
    list_filter = ('role', 'statut', 'date_inscription', 'notifications_email')
    search_fields = ('utilisateur__username', 'utilisateur__email', 'utilisateur__first_name', 'utilisateur__last_name')
    date_hierarchy = 'date_inscription'
    ordering = ('-date_inscription',)
    readonly_fields = ('date_inscription', 'nombre_articles', 'nombre_commentaires')
    
    fieldsets = (
        ('Informations utilisateur', {
            'fields': ('utilisateur', 'role', 'statut')
        }),
        ('Informations personnelles', {
            'fields': ('bio', 'avatar')
        }),
        ('Statistiques', {
            'fields': ('date_inscription', 'derniere_connexion', 'nombre_articles', 'nombre_commentaires'),
            'classes': ('collapse',)
        }),
        ('Paramètres de notification', {
            'fields': ('notifications_email', 'notifications_nouveaux_articles', 'notifications_commentaires'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activer_utilisateurs', 'suspendre_utilisateurs', 'promouvoir_redacteurs']
    
    def activer_utilisateurs(self, request, queryset):
        count = queryset.update(statut='actif')
        self.message_user(request, f'{count} utilisateur(s) activé(s).')
    activer_utilisateurs.short_description = "Activer les utilisateurs sélectionnés"
    
    def suspendre_utilisateurs(self, request, queryset):
        count = queryset.update(statut='suspendu')
        self.message_user(request, f'{count} utilisateur(s) suspendu(s).')
    suspendre_utilisateurs.short_description = "Suspendre les utilisateurs sélectionnés"
    
    def promouvoir_redacteurs(self, request, queryset):
        count = queryset.filter(role='lecteur').update(role='redacteur')
        self.message_user(request, f'{count} utilisateur(s) promu(s) au rang de rédacteur.')
    promouvoir_redacteurs.short_description = "Promouvoir les lecteurs en rédacteurs"


# Configuration étendue de l'admin pour les utilisateurs
class ProfilUtilisateurInline(admin.StackedInline):
    model = ProfilUtilisateur
    can_delete = False
    verbose_name_plural = 'Profil'
    fk_name = 'utilisateur'


class UtilisateurEtenduAdmin(UserAdmin):
    inlines = (ProfilUtilisateurInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role', 'get_statut')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'profil__role', 'profil__statut')
    
    def get_role(self, obj):
        if hasattr(obj, 'profil'):
            return obj.profil.get_role_display()
        return 'Aucun profil'
    get_role.short_description = 'Rôle'
    
    def get_statut(self, obj):
        if hasattr(obj, 'profil'):
            return obj.profil.get_statut_display()
        return 'Aucun profil'
    get_statut.short_description = 'Statut'


# Désinscrire l'admin User par défaut et inscrire le nouveau
admin.site.unregister(User)
admin.site.register(User, UtilisateurEtenduAdmin)

# Personnalisation du site admin
admin.site.site_header = "Administration du Blog"
admin.site.site_title = "Blog Admin"
admin.site.index_title = "Panneau d'administration"
