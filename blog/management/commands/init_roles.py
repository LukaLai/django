"""
Commande Django pour initialiser le système de rôles et permissions
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from blog.models import ProfilUtilisateur, GestionnaireRoles


class Command(BaseCommand):
    help = 'Initialise le système de rôles et permissions du blog'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-admin',
            action='store_true',
            help='Créer un utilisateur administrateur par défaut',
        )
        parser.add_argument(
            '--admin-username',
            type=str,
            default='admin',
            help='Nom d\'utilisateur pour l\'administrateur (défaut: admin)',
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@example.com',
            help='Email pour l\'administrateur',
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123',
            help='Mot de passe pour l\'administrateur (défaut: admin123)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Initialisation du système de rôles et permissions...')
        )

        # 1. Créer les groupes et permissions
        self.stdout.write('Création des groupes de rôles...')
        try:
            GestionnaireRoles.creer_groupes_par_defaut()
            self.stdout.write(
                self.style.SUCCESS('✓ Groupes de rôles créés avec succès')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Erreur lors de la création des groupes: {e}')
            )

        # 2. Créer un administrateur si demandé
        if options['create_admin']:
            self.stdout.write('Création de l\'utilisateur administrateur...')
            try:
                username = options['admin_username']
                email = options['admin_email']
                password = options['admin_password']

                # Vérifier si l'utilisateur existe déjà
                if User.objects.filter(username=username).exists():
                    self.stdout.write(
                        self.style.WARNING(f'L\'utilisateur {username} existe déjà')
                    )
                else:
                    # Créer l'utilisateur
                    admin_user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        is_staff=True,
                        is_superuser=True
                    )

                    # Le profil est créé automatiquement via le signal
                    # Assigner le rôle administrateur
                    GestionnaireRoles.assigner_role_utilisateur(admin_user, 'administrateur')

                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Administrateur {username} créé avec succès')
                    )
                    self.stdout.write(f'  Email: {email}')
                    self.stdout.write(f'  Mot de passe: {password}')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Erreur lors de la création de l\'administrateur: {e}')
                )

        # 3. Afficher un résumé
        self.stdout.write('\n' + '='*50)
        self.stdout.write('RÉSUMÉ DU SYSTÈME DE RÔLES')
        self.stdout.write('='*50)

        roles_descriptions = {
            'lecteur': 'Peut lire les articles et commenter',
            'redacteur': 'Peut écrire et publier ses propres articles',
            'moderateur': 'Peut modérer les commentaires',
            'editeur': 'Peut gérer tous les articles et catégories',
            'administrateur': 'Accès complet à l\'administration'
        }

        for role, description in roles_descriptions.items():
            self.stdout.write(f'• {role.capitalize()}: {description}')

        self.stdout.write('\n' + '='*50)
        self.stdout.write('COMMANDES UTILES')
        self.stdout.write('='*50)
        self.stdout.write('• Créer les migrations: python manage.py makemigrations')
        self.stdout.write('• Appliquer les migrations: python manage.py migrate')
        self.stdout.write('• Assigner un rôle à un utilisateur:')
        self.stdout.write('  python manage.py assign_role <username> <role>')

        self.stdout.write(
            self.style.SUCCESS('\n✓ Initialisation terminée avec succès!')
        )
