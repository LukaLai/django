"""
Commande Django pour assigner un rôle à un utilisateur
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from blog.models import GestionnaireRoles, ProfilUtilisateur


class Command(BaseCommand):
    help = 'Assigne un rôle à un utilisateur'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nom d\'utilisateur')
        parser.add_argument('role', type=str, help='Rôle à assigner')
        parser.add_argument(
            '--list-roles',
            action='store_true',
            help='Afficher la liste des rôles disponibles',
        )

    def handle(self, *args, **options):
        if options['list_roles']:
            self.stdout.write('Rôles disponibles:')
            for role, description in ProfilUtilisateur.ROLES_CHOICES:
                self.stdout.write(f'• {role}: {description}')
            return

        username = options['username']
        role = options['role']

        # Vérifier que le rôle existe
        roles_valides = [r[0] for r in ProfilUtilisateur.ROLES_CHOICES]
        if role not in roles_valides:
            raise CommandError(
                f'Rôle "{role}" invalide. Rôles disponibles: {", ".join(roles_valides)}'
            )

        # Vérifier que l'utilisateur existe
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'Utilisateur "{username}" non trouvé')

        # Assigner le rôle
        try:
            GestionnaireRoles.assigner_role_utilisateur(user, role)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Rôle "{role}" assigné à l\'utilisateur "{username}"'
                )
            )

            # Afficher les permissions de l'utilisateur
            if hasattr(user, 'profil'):
                profil = user.profil
                self.stdout.write(f'\nPermissions de {username}:')
                self.stdout.write(f'• Peut publier des articles: {profil.peut_publier_articles()}')
                self.stdout.write(f'• Peut modérer les commentaires: {profil.peut_moderer_commentaires()}')
                self.stdout.write(f'• Peut gérer les catégories: {profil.peut_gerer_categories()}')
                self.stdout.write(f'• Peut gérer les utilisateurs: {profil.peut_gerer_utilisateurs()}')
                self.stdout.write(f'• Peut voir les statistiques: {profil.peut_voir_statistiques()}')

        except Exception as e:
            raise CommandError(f'Erreur lors de l\'assignation du rôle: {e}')
