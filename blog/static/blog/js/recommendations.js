/**
 * Script pour le système de recommandations intelligentes
 * Améliore l'interaction utilisateur et l'engagement
 */

class RecommendationSystem {
    constructor() {
        this.timeSpent = 0;
        this.startTime = Date.now();
        this.isVisible = true;
        this.init();
    }

    init() {
        this.trackTimeSpent();
        this.enhanceRecommendationCards();
        this.addScrollAnimations();
        this.trackRecommendationClicks();
    }

    /**
     * Suivi du temps passé sur la page
     */
    trackTimeSpent() {
        // Écouter la visibilité de la page
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.isVisible = false;
                this.updateTimeSpent();
            } else {
                this.isVisible = true;
                this.startTime = Date.now();
            }
        });

        // Envoyer les données avant de quitter la page
        window.addEventListener('beforeunload', () => {
            this.updateTimeSpent();
        });

        // Mettre à jour toutes les 30 secondes
        setInterval(() => {
            if (this.isVisible) {
                this.updateTimeSpent();
            }
        }, 30000);
    }

    updateTimeSpent() {
        if (this.isVisible) {
            this.timeSpent += (Date.now() - this.startTime) / 1000;
            this.startTime = Date.now();

            // Ici, vous pourriez envoyer les données au serveur
            // pour améliorer les recommandations futures
            console.log(`Temps passé: ${Math.round(this.timeSpent)}s`);
        }
    }

    /**
     * Améliore l'interactivité des cartes de recommandation
     */
    enhanceRecommendationCards() {
        const recommendationCards = document.querySelectorAll('.recommendation-card');
        
        recommendationCards.forEach(card => {
            // Effet de tilt au survol
            card.addEventListener('mouseenter', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = (y - centerY) / 10;
                const rotateY = (centerX - x) / 10;
                
                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
                card.style.transition = 'transform 0.1s ease-out';
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
                card.style.transition = 'transform 0.3s ease-out';
            });

            // Effet de clic avec animation
            card.addEventListener('mousedown', () => {
                card.style.transform += ' scale(0.98)';
            });

            card.addEventListener('mouseup', () => {
                card.style.transform = card.style.transform.replace(' scale(0.98)', '');
            });
        });
    }

    /**
     * Animations au scroll pour les recommandations
     */
    addScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    
                    // Animation staggerée pour les cartes
                    const cards = entry.target.querySelectorAll('.recommendation-card');
                    cards.forEach((card, index) => {
                        setTimeout(() => {
                            card.classList.add('slide-in');
                        }, index * 100);
                    });
                }
            });
        }, observerOptions);

        // Observer les sections de recommandations
        const recommendationSections = document.querySelectorAll('.recommendations-section');
        recommendationSections.forEach(section => {
            observer.observe(section);
        });
    }

    /**
     * Suivi des clics sur les recommandations
     */
    trackRecommendationClicks() {
        const recommendationLinks = document.querySelectorAll('.recommendation-card-link');
        
        recommendationLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                // Récupérer les informations de l'article
                const card = e.currentTarget.querySelector('.recommendation-card');
                const title = card.querySelector('.recommendation-title')?.textContent;
                const categories = card.querySelectorAll('.recommendation-category');
                
                // Analytics personnalisées
                this.logRecommendationClick({
                    articleTitle: title,
                    categories: Array.from(categories).map(cat => cat.textContent.trim()),
                    timeOnPage: Math.round(this.timeSpent),
                    timestamp: new Date().toISOString()
                });

                // Effet visuel de feedback
                this.addClickFeedback(card);
            });
        });
    }

    logRecommendationClick(data) {
        console.log('Clic sur recommandation:', data);
        
        // Ici vous pourriez envoyer ces données à votre serveur
        // pour améliorer l'algorithme de recommandation
        /*
        fetch('/api/track-recommendation-click/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });
        */
    }

    addClickFeedback(card) {
        // Créer un effet de ripple
        const ripple = document.createElement('div');
        ripple.classList.add('ripple-effect');
        
        const rect = card.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = '50%';
        ripple.style.top = '50%';
        ripple.style.transform = 'translate(-50%, -50%)';
        
        card.style.position = 'relative';
        card.appendChild(ripple);
        
        // Supprimer l'effet après l'animation
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    /**
     * Système de recommandations en temps réel
     */
    updateRecommendationsRealTime() {
        // Cette fonction pourrait être appelée périodiquement
        // pour mettre à jour les recommandations basées sur le comportement actuel
        
        setInterval(() => {
            if (this.timeSpent > 120) { // Si l'utilisateur passe plus de 2 minutes
                this.fetchUpdatedRecommendations();
            }
        }, 60000); // Vérifier chaque minute
    }

    fetchUpdatedRecommendations() {
        // Simuler une mise à jour des recommandations
        console.log('Mise à jour des recommandations basée sur le comportement...');
        
        // Ici vous pourriez faire un appel AJAX pour obtenir
        // de nouvelles recommandations basées sur le temps passé et les interactions
    }
}

// Styles CSS additionnels pour les animations
const additionalStyles = `
<style>
.recommendations-section {
    opacity: 0;
    transform: translateY(30px);
    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.recommendations-section.animate-in {
    opacity: 1;
    transform: translateY(0);
}

.recommendation-card {
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.recommendation-card.slide-in {
    opacity: 1;
    transform: translateY(0);
}

.ripple-effect {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.6);
    pointer-events: none;
    animation: ripple 0.6s ease-out;
    z-index: 10;
}

@keyframes ripple {
    0% {
        transform: translate(-50%, -50%) scale(0);
        opacity: 1;
    }
    100% {
        transform: translate(-50%, -50%) scale(4);
        opacity: 0;
    }
}

/* Amélioration de l'accessibilité */
.recommendation-card:focus {
    outline: 3px solid #007cba;
    outline-offset: 2px;
}

.recommendation-card-link:focus {
    outline: none;
}

/* Animation de chargement pour les recommandations */
.recommendations-loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-top: 4px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Responsive amélioré */
@media (max-width: 768px) {
    .recommendations-grid {
        grid-template-columns: 1fr;
        gap: 15px;
    }
    
    .recommendation-card {
        margin: 0 auto;
        max-width: 350px;
    }
}

@media (prefers-reduced-motion: reduce) {
    .recommendation-card,
    .recommendations-section,
    .ripple-effect {
        transition: none;
        animation: none;
    }
}
</style>
`;

// Injecter les styles additionnels
document.head.insertAdjacentHTML('beforeend', additionalStyles);

// Initialiser le système quand le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    new RecommendationSystem();
});

// Fonction utilitaire pour obtenir le token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
