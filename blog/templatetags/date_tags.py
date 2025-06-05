from django import template
from django.utils import timezone
from django.utils.translation import gettext as _
from datetime import datetime, timedelta
import locale

register = template.Library()

@register.filter
def time_since(value):
    """
    Affiche une date de manière relative et conviviale
    """
    if not value:
        return ""
    
    now = timezone.now()
    if timezone.is_naive(value):
        value = timezone.make_aware(value)
    
    diff = now - value
    
    # Si c'est dans le futur
    if diff.total_seconds() < 0:
        return _("Dans le futur")
    
    seconds = diff.total_seconds()
    
    # Moins d'une minute
    if seconds < 60:
        return _("À l'instant")
    
    # Moins d'une heure
    elif seconds < 3600:
        minutes = int(seconds // 60)
        if minutes == 1:
            return _("Il y a 1 minute")
        return _("Il y a {} minutes").format(minutes)
    
    # Moins d'un jour
    elif seconds < 86400:
        hours = int(seconds // 3600)
        if hours == 1:
            return _("Il y a 1 heure")
        return _("Il y a {} heures").format(hours)
    
    # Hier
    elif seconds < 172800:  # 2 jours
        return _("Hier à {}").format(value.strftime("%H:%M"))
    
    # Moins d'une semaine
    elif seconds < 604800:  # 7 jours
        days = int(seconds // 86400)
        day_name = value.strftime("%A")
        # Traduire le nom du jour
        day_names = {
            'Monday': _('Lundi'),
            'Tuesday': _('Mardi'),
            'Wednesday': _('Mercredi'),
            'Thursday': _('Jeudi'),
            'Friday': _('Vendredi'),
            'Saturday': _('Samedi'),
            'Sunday': _('Dimanche')
        }
        day_translated = day_names.get(day_name, day_name)
        return _("{} à {}").format(day_translated, value.strftime("%H:%M"))
    
    # Moins d'un mois
    elif seconds < 2592000:  # 30 jours
        weeks = int(seconds // 604800)
        if weeks == 1:
            return _("La semaine dernière")
        return _("Il y a {} semaines").format(weeks)
    
    # Moins d'un an
    elif seconds < 31536000:  # 365 jours
        months = int(seconds // 2592000)
        if months == 1:
            return _("Le mois dernier")
        return _("Il y a {} mois").format(months)
    
    # Plus d'un an
    else:
        years = int(seconds // 31536000)
        if years == 1:
            return _("L'année dernière")
        return _("Il y a {} ans").format(years)

@register.filter
def precise_date(value):
    """
    Affiche une date précise avec format complet
    """
    if not value:
        return ""
    
    try:
        # Format français complet
        return value.strftime("%d %B %Y à %H:%M")
    except:
        return str(value)

@register.filter
def smart_date(value):
    """
    Affiche une date intelligente : relative si récente, précise si ancienne
    """
    if not value:
        return ""
    
    now = timezone.now()
    if timezone.is_naive(value):
        value = timezone.make_aware(value)
    
    diff = now - value
    
    # Si moins de 7 jours, affichage relatif
    if diff.total_seconds() < 604800:
        return time_since(value)
    else:
        # Sinon affichage précis
        return precise_date(value)

@register.inclusion_tag('blog/date_display.html')
def date_with_tooltip(date_value, css_class=""):
    """
    Affiche une date avec tooltip informatif
    """
    return {
        'date_value': date_value,
        'relative_date': time_since(date_value),
        'precise_date': precise_date(date_value),
        'css_class': css_class
    }
