from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count, Q
from collections import Counter
import re
import math


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icone = models.CharField(max_length=100, blank=True, null=True, help_text="Nom de l'icône ou code SVG")
    couleur = models.CharField(max_length=20, blank=True, null=True, help_text="Code couleur hexadécimal, ex: #007cba")

    def __str__(self):
        return self.nom
    
class Article(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    auteur = models.CharField(max_length=100)
    date_creation = models.DateTimeField(default=timezone.now)
    categories = models.ManyToManyField(Categorie, related_name='articles')
    image_base64 = models.TextField(blank=True, null=True)
    vues = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.titre
    
    def temps_lecture_estime(self):
        """
        Calcule le temps de lecture estimé en minutes
        Basé sur une vitesse de lecture moyenne de 200 mots par minute
        """
        if not self.contenu:
            return 0
        
        # Nettoyer le contenu HTML et compter les mots
        contenu_propre = re.sub(r'<[^>]+>', '', self.contenu)  # Supprimer les balises HTML
        contenu_propre = re.sub(r'\s+', ' ', contenu_propre)   # Normaliser les espaces
        mots = len(contenu_propre.split())
        
        # Calcul basé sur 200 mots par minute (vitesse de lecture moyenne)
        minutes = math.ceil(mots / 200)
        return max(1, minutes)  # Minimum 1 minute
    
    def temps_lecture_texte(self):
        """
        Retourne le texte formaté du temps de lecture
        """
        temps = self.temps_lecture_estime()
        if temps == 1:
            return _("1 minute de lecture")
        else:
            return _("%(temps)d minutes de lecture") % {'temps': temps}
    
    def get_mots_cles(self):
        """
        Extrait les mots-clés du titre et du contenu pour l'analyse de similarité
        """
        contenu_propre = re.sub(r'<[^>]+>', '', self.contenu)
        texte_complet = f"{self.titre} {contenu_propre}".lower()
        # Supprimer la ponctuation et les mots vides communs
        mots_vides = {'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'ou', 'mais', 'donc', 'car', 'ni', 'or', 'ce', 'ces', 'cet', 'cette', 'pour', 'par', 'avec', 'sans', 'sur', 'sous', 'dans', 'vers', 'chez', 'que', 'qui', 'quoi', 'dont', 'où', 'comment', 'pourquoi', 'quand', 'est', 'sont', 'être', 'avoir', 'il', 'elle', 'nous', 'vous', 'ils', 'elles'}
        mots = re.findall(r'\b[a-zA-Zàâäéèêëïîôùûüÿñç]{3,}\b', texte_complet)
        return [mot for mot in mots if mot not in mots_vides]

    def get_articles_similaires(self, limite=5):
        """
        Trouve les articles similaires basés sur les catégories et les mots-clés
        """
        if not self.pk:
            return Article.objects.none()

        # Articles de mêmes catégories
        articles_memes_categories = Article.objects.filter(
            categories__in=self.categories.all()
        ).exclude(pk=self.pk).distinct()

        # Calculer la similarité basée sur les mots-clés
        mes_mots_cles = self.get_mots_cles()
        articles_avec_score = []

        for article in articles_memes_categories:
            ses_mots_cles = article.get_mots_cles()
            
            # Calcul de similarité basé sur les mots communs
            mots_communs = set(mes_mots_cles) & set(ses_mots_cles)
            score_mots = len(mots_communs) / max(len(set(mes_mots_cles + ses_mots_cles)), 1)
            
            # Bonus pour les catégories communes
            categories_communes = self.categories.filter(id__in=article.categories.all()).count()
            score_categories = categories_communes / max(self.categories.count(), 1)
            
            # Score final
            score_final = (score_mots * 0.7) + (score_categories * 0.3)
            
            if score_final > 0:
                articles_avec_score.append((article, score_final))

        # Trier par score et prendre les meilleurs
        articles_avec_score.sort(key=lambda x: x[1], reverse=True)
        return [article for article, score in articles_avec_score[:limite]]
    
    class Meta:
        ordering = ['-date_creation']


class InteractionUtilisateur(models.Model):
    """
    Modèle pour suivre les interactions des utilisateurs avec les articles
    """
    TYPE_INTERACTION_CHOICES = [
        ('vue', 'Vue'),
        ('like', 'J\'aime'),
        ('commentaire', 'Commentaire'),
        ('partage', 'Partage'),
    ]
    
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    type_interaction = models.CharField(max_length=20, choices=TYPE_INTERACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    date_interaction = models.DateTimeField(default=timezone.now)
    temps_lecture = models.PositiveIntegerField(null=True, blank=True, help_text="Temps passé en secondes")

    class Meta:
        unique_together = ['utilisateur', 'article', 'type_interaction', 'session_key']
        ordering = ['-date_interaction']

    def __str__(self):
        utilisateur_str = self.utilisateur.username if self.utilisateur else f"Anonyme ({self.session_key[:8]})"
        return f"{utilisateur_str} - {self.type_interaction} - {self.article.titre}"


class RecommandationEngine:
    """
    Moteur de recommandation intelligent
    """
    
    @staticmethod
    def get_recommendations_for_user(user=None, session_key=None, limite=6):
        """
        Obtient des recommandations personnalisées pour un utilisateur
        """
        recommendations = []
        
        # 1. Recommandations basées sur l'historique de l'utilisateur
        if user and user.is_authenticated:
            user_recommendations = RecommandationEngine._get_user_based_recommendations(user, limite//2)
            recommendations.extend(user_recommendations)
        elif session_key:
            session_recommendations = RecommandationEngine._get_session_based_recommendations(session_key, limite//2)
            recommendations.extend(session_recommendations)
        
        # 2. Compléter avec les articles populaires
        if len(recommendations) < limite:
            popular_articles = RecommandationEngine._get_popular_articles(limite - len(recommendations))
            # Éviter les doublons
            existing_ids = [art.id for art in recommendations]
            for article in popular_articles:
                if article.id not in existing_ids:
                    recommendations.append(article)
        
        return recommendations[:limite]
    
    @staticmethod
    def _get_user_based_recommendations(user, limite):
        """
        Recommandations basées sur l'historique de l'utilisateur
        """
        # Catégories préférées de l'utilisateur
        interactions = InteractionUtilisateur.objects.filter(
            utilisateur=user,
            type_interaction__in=['vue', 'like', 'commentaire']
        ).select_related('article')
        
        if not interactions.exists():
            return []
        
        # Analyser les préférences
        categories_vues = []
        for interaction in interactions:
            categories_vues.extend(list(interaction.article.categories.all()))
        
        # Compter les catégories les plus populaires
        categories_count = Counter(categories_vues)
        categories_preferees = [cat for cat, count in categories_count.most_common(5)]
        
        # Articles vus par l'utilisateur
        articles_vus = [interaction.article.id for interaction in interactions]
        
        # Recommander des articles des mêmes catégories
        articles_recommandes = Article.objects.filter(
            categories__in=categories_preferees
        ).exclude(
            id__in=articles_vus
        ).distinct().order_by('-vues', '-date_creation')[:limite]
        
        return list(articles_recommandes)
    
    @staticmethod
    def _get_session_based_recommendations(session_key, limite):
        """
        Recommandations basées sur la session anonyme
        """
        interactions = InteractionUtilisateur.objects.filter(
            session_key=session_key,
            type_interaction='vue'
        ).select_related('article')
        
        if not interactions.exists():
            return []
        
        # Même logique que pour les utilisateurs authentifiés
        categories_vues = []
        articles_vus = []
        
        for interaction in interactions:
            categories_vues.extend(list(interaction.article.categories.all()))
            articles_vus.append(interaction.article.id)
        
        categories_count = Counter(categories_vues)
        categories_preferees = [cat for cat, count in categories_count.most_common(3)]
        
        articles_recommandes = Article.objects.filter(
            categories__in=categories_preferees
        ).exclude(
            id__in=articles_vus
        ).distinct().order_by('-vues', '-date_creation')[:limite]
        
        return list(articles_recommandes)
    
    @staticmethod
    def _get_popular_articles(limite):
        """
        Articles populaires basés sur les vues et interactions récentes
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # Articles populaires des 30 derniers jours
        date_limite = timezone.now() - timedelta(days=30)
        
        return Article.objects.annotate(
            interactions_count=Count('interactionutilisateur', filter=Q(interactionutilisateur__date_interaction__gte=date_limite))
        ).order_by('-interactions_count', '-vues', '-date_creation')[:limite]


class Commentaire(models.Model):
    article = models.ForeignKey(Article, related_name='commentaires', on_delete=models.CASCADE)
    auteur = models.CharField(max_length=100)
    contenu = models.TextField()
    date_creation = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Commentaire de {self.auteur} sur {self.article.titre}"

    class Meta:
        ordering = ['-date_creation']


class ProfilUtilisateur(models.Model):
    """
    Profil étendu pour les utilisateurs avec système de rôles
    """
    ROLES_CHOICES = [
        ('lecteur', 'Lecteur'),
        ('redacteur', 'Rédacteur'),
        ('moderateur', 'Modérateur'),
        ('editeur', 'Éditeur'),
        ('administrateur', 'Administrateur'),
    ]
    
    STATUTS_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('suspendu', 'Suspendu'),
        ('banni', 'Banni'),
    ]
    
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    role = models.CharField(max_length=20, choices=ROLES_CHOICES, default='lecteur')
    statut = models.CharField(max_length=20, choices=STATUTS_CHOICES, default='actif')
    bio = models.TextField(blank=True, null=True, help_text="Biographie de l'utilisateur")
    avatar = models.TextField(blank=True, null=True, help_text="Avatar en base64")
    date_inscription = models.DateTimeField(auto_now_add=True)
    derniere_connexion = models.DateTimeField(null=True, blank=True)
    nombre_articles = models.PositiveIntegerField(default=0)
    nombre_commentaires = models.PositiveIntegerField(default=0)
    
    # Paramètres de notification
    notifications_email = models.BooleanField(default=True)
    notifications_nouveaux_articles = models.BooleanField(default=True)
    notifications_commentaires = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
        permissions = [
            ("can_moderate_comments", "Peut modérer les commentaires"),
            ("can_manage_categories", "Peut gérer les catégories"),
            ("can_publish_articles", "Peut publier des articles"),
            ("can_edit_all_articles", "Peut éditer tous les articles"),
            ("can_view_statistics", "Peut voir les statistiques"),
            ("can_manage_users", "Peut gérer les utilisateurs"),
        ]
    
    def __str__(self):
        return f"{self.utilisateur.username} ({self.get_role_display()})"
    
    def peut_publier_articles(self):
        """Vérifie si l'utilisateur peut publier des articles"""
        return self.role in ['redacteur', 'editeur', 'administrateur'] and self.statut == 'actif'
    
    def peut_moderer_commentaires(self):
        """Vérifie si l'utilisateur peut modérer les commentaires"""
        return self.role in ['moderateur', 'editeur', 'administrateur'] and self.statut == 'actif'
    
    def peut_gerer_categories(self):
        """Vérifie si l'utilisateur peut gérer les catégories"""
        return self.role in ['editeur', 'administrateur'] and self.statut == 'actif'
    
    def peut_gerer_utilisateurs(self):
        """Vérifie si l'utilisateur peut gérer les autres utilisateurs"""
        return self.role == 'administrateur' and self.statut == 'actif'
    
    def peut_voir_statistiques(self):
        """Vérifie si l'utilisateur peut voir les statistiques"""
        return self.role in ['editeur', 'administrateur'] and self.statut == 'actif'


@receiver(post_save, sender=User)
def creer_profil_utilisateur(sender, instance, created, **kwargs):
    """Créer automatiquement un profil quand un utilisateur est créé"""
    if created:
        ProfilUtilisateur.objects.create(utilisateur=instance)


@receiver(post_save, sender=User)
def sauvegarder_profil_utilisateur(sender, instance, **kwargs):
    """Sauvegarder le profil quand l'utilisateur est sauvegardé"""
    if hasattr(instance, 'profil'):
        instance.profil.save()


class GestionnaireRoles:
    """
    Classe utilitaire pour gérer les rôles et permissions
    """
    
    @staticmethod
    def creer_groupes_par_defaut():
        """Créer les groupes de rôles par défaut avec leurs permissions"""
        
        # Définir les permissions pour chaque rôle
        permissions_par_role = {
            'Lecteurs': [],  # Permissions de base seulement
            'Rédacteurs': [
                'can_publish_articles',
                'add_article',
                'change_article',  # Seulement ses propres articles
            ],
            'Modérateurs': [
                'can_moderate_comments',
                'add_commentaire',
                'change_commentaire',
                'delete_commentaire',
                'view_commentaire',
            ],
            'Éditeurs': [
                'can_publish_articles',
                'can_edit_all_articles',
                'can_manage_categories',
                'can_view_statistics',
                'add_article',
                'change_article',
                'delete_article',
                'view_article',
                'add_categorie',
                'change_categorie',
                'delete_categorie',
                'view_categorie',
            ],
            'Administrateurs': [
                'can_manage_users',
                'can_view_statistics',
                'can_edit_all_articles',
                'can_manage_categories',
                'can_moderate_comments',
                'can_publish_articles',
            ]
        }
        
        for nom_groupe, permissions in permissions_par_role.items():
            groupe, created = Group.objects.get_or_create(name=nom_groupe)
            if created:
                print(f"Groupe '{nom_groupe}' créé")
            
            # Ajouter les permissions au groupe
            for perm_name in permissions:
                try:
                    if perm_name.startswith('can_'):
                        # Permission personnalisée
                        permission = Permission.objects.get(
                            codename=perm_name,
                            content_type=ContentType.objects.get_for_model(ProfilUtilisateur)
                        )
                    else:
                        # Permission Django standard
                        model_name = 'article' if 'article' in perm_name else \
                                   'categorie' if 'categorie' in perm_name else \
                                   'commentaire' if 'commentaire' in perm_name else None
                        
                        if model_name:
                            content_type = ContentType.objects.get(app_label='blog', model=model_name)
                            permission = Permission.objects.get(
                                codename=perm_name,
                                content_type=content_type
                            )
                        else:
                            continue
                    
                    groupe.permissions.add(permission)
                except Permission.DoesNotExist:
                    print(f"Permission '{perm_name}' non trouvée")
    
    @staticmethod
    def assigner_role_utilisateur(utilisateur, role):
        """Assigner un rôle à un utilisateur"""
        # Retirer l'utilisateur de tous les groupes de rôles
        groupes_roles = ['Lecteurs', 'Rédacteurs', 'Modérateurs', 'Éditeurs', 'Administrateurs']
        for groupe_name in groupes_roles:
            try:
                groupe = Group.objects.get(name=groupe_name)
                utilisateur.groups.remove(groupe)
            except Group.DoesNotExist:
                pass
        
        # Assigner le nouveau rôle
        mapping_roles = {
            'lecteur': 'Lecteurs',
            'redacteur': 'Rédacteurs',
            'moderateur': 'Modérateurs',
            'editeur': 'Éditeurs',
            'administrateur': 'Administrateurs',
        }
        
        nom_groupe = mapping_roles.get(role)
        if nom_groupe:
            try:
                groupe = Group.objects.get(name=nom_groupe)
                utilisateur.groups.add(groupe)
                
                # Mettre à jour le profil
                if hasattr(utilisateur, 'profil'):
                    utilisateur.profil.role = role
                    utilisateur.profil.save()
                    
            except Group.DoesNotExist:
                print(f"Groupe '{nom_groupe}' non trouvé")