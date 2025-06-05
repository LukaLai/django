from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from .models import InteractionUtilisateur, Article
import logging

logger = logging.getLogger(__name__)

class RecommendationMiddleware(MiddlewareMixin):
    """
    Middleware pour enregistrer automatiquement les interactions utilisateurs
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Enregistre les vues d'articles pour le système de recommandation
        """
        try:
            # Vérifier si c'est une vue de détail d'article
            url_name = resolve(request.path_info).url_name
            
            if url_name == 'detail_article' and 'article_id' in view_kwargs:
                article_id = view_kwargs['article_id']
                
                try:
                    article = Article.objects.get(id=article_id)
                    
                    # Incrémenter le compteur de vues
                    article.vues += 1
                    article.save(update_fields=['vues'])
                    
                    # Enregistrer l'interaction
                    user = request.user if request.user.is_authenticated else None
                    session_key = request.session.session_key
                    
                    # Créer la session si elle n'existe pas
                    if not session_key:
                        request.session.create()
                        session_key = request.session.session_key
                    
                    # Obtenir l'adresse IP
                    ip_address = self.get_client_ip(request)
                    
                    # Enregistrer l'interaction (éviter les doublons)
                    interaction, created = InteractionUtilisateur.objects.get_or_create(
                        utilisateur=user,
                        article=article,
                        type_interaction='vue',
                        session_key=session_key if not user else None,
                        defaults={
                            'ip_address': ip_address,
                        }
                    )
                    
                    if created:
                        logger.info(f"Interaction vue enregistrée pour l'article {article.titre}")
                    
                except Article.DoesNotExist:
                    logger.warning(f"Article avec ID {article_id} introuvable")
                except Exception as e:
                    logger.error(f"Erreur lors de l'enregistrement de l'interaction: {e}")
                    
        except Exception as e:
            logger.error(f"Erreur dans RecommendationMiddleware: {e}")
        
        return None
    
    def get_client_ip(self, request):
        """
        Obtient l'adresse IP du client
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
