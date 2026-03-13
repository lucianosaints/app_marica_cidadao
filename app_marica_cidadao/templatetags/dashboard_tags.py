from django import template
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
import json
from app_marica_cidadao.models import RelatoZeladoria

register = template.Library()

@register.simple_tag
def get_admin_dashboard_stats(bairro=None):
    """
    Retorna as estatísticas para o mini-dashboard da index do admin.
    Usa a mesma lógica centralizada do Dashboard Premium.
    """
    from app_marica_cidadao.utils import get_dashboard_stats
    return get_dashboard_stats(bairro)
