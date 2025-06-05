from django.urls import path, reverse
from . import views
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    def get_success_url(self):
        return reverse('home')

urlpatterns = [
    path('', views.home, name='home'),
    path('articles/', views.articles, name='articles'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('ajouter/', views.ajouter_article, name='ajouter_article'),
    path('modifier/<int:article_id>/', views.modifier_article, name='modifier_article'),
    path('ajouter_commentaire/<int:article_id>/', views.ajouter_commentaire, name='ajouter_commentaire'),
    path('ajouter_categorie/', views.ajouter_categorie, name='ajouter_categorie'),
    path('categories/', views.liste_categories, name='liste_categories'),
    path('categories/supprimer/<int:categorie_id>/', views.supprimer_categorie, name='supprimer_categorie'),    path('profile/', views.profile, name='profile'),
    path('login/', CustomLoginView.as_view(template_name='blog/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.deconnexion, name='logout'),
    path('test-log/', views.test_log_view, name='test_log'),
      # URLs pour la gestion des utilisateurs et rôles
    path('gestion-utilisateurs/', views.gestion_utilisateurs, name='gestion_utilisateurs'),
    path('modifier-role/', views.modifier_role_utilisateur, name='modifier_role_utilisateur'),
    path('modifier-statut/', views.modifier_statut_utilisateur, name='modifier_statut_utilisateur'),
    path('mon-profil/', views.mon_profil, name='mon_profil'),
    path('statistiques-roles/', views.statistiques_roles, name='statistiques_roles'),
    path('utilisateur/<int:user_id>/', views.voir_profil_utilisateur, name='voir_profil_utilisateur'),
      # URLs pour ChatGPT
    path('chatgpt/', views.chatgpt_view, name='chatgpt'),
    path('api/chatgpt/', views.chatgpt_api, name='chatgpt_api'),
    path('api/generate-article/', views.generate_article_ai, name='generate_article_ai'),
]