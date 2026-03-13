from django import template
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
import json
from app_marica_cidadao.models import RelatoZeladoria

register = template.Library()

@register.simple_tag
def get_admin_dashboard_stats():
    # 1. Estatísticas de Status
    status_stats = RelatoZeladoria.objects.values('status_atual').annotate(total=Count('id'))
    
    # 2. Estatísticas de Categoria
    categoria_stats = RelatoZeladoria.objects.values('categoria__nome').annotate(total=Count('id')).order_by('-total')
    
    # 3. Evolução dos últimos 30 dias
    trinta_dias_atras = timezone.now() - timedelta(days=30)
    evolucao_stats = RelatoZeladoria.objects.filter(
        criado_em__gte=trinta_dias_atras
    ).annotate(
        data=TruncDate('criado_em')
    ).values('data').annotate(
        total=Count('id')
    ).order_by('data')

    # 4. Geocalização para Heatmap
    coordenadas = RelatoZeladoria.objects.exclude(
        latitude__isnull=True
    ).exclude(
        longitude__isnull=True
    ).values('latitude', 'longitude')

    # 5. KPIs
    stats = {
        'status_stats_json': json.dumps(list(status_stats)),
        'categoria_stats_json': json.dumps(list(categoria_stats)),
        'evolucao_stats_json': json.dumps([
            {'data': item['data'].strftime('%d/%m'), 'total': item['total']} 
            for item in evolucao_stats
        ]),
        'heatmap_data_json': json.dumps(list(coordenadas)),
        'total_relatos': RelatoZeladoria.objects.count(),
        'resolvidos': RelatoZeladoria.objects.filter(status_atual='resolvido').count(),
        'pendentes': RelatoZeladoria.objects.filter(status_atual='recebido').count(),
        'em_andamento': RelatoZeladoria.objects.filter(status_atual='em_progresso').count(),
    }
    return stats
