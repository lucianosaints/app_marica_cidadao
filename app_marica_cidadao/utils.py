import json
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from .models import RelatoZeladoria

def get_dashboard_stats(bairro_selecionado=None):
    """
    Centraliza a lógica de cálculo de estatísticas para o dashboard.
    Pode ser usada tanto no Admin customizado quanto na view de Dashboards Premium.
    """
    qs_base = RelatoZeladoria.objects.all()
    
    if bairro_selecionado:
        qs_base = qs_base.filter(bairro=bairro_selecionado)
        
    # 1. Estatísticas de Status
    status_stats = qs_base.values('status_atual').annotate(total=Count('id'))
    
    # 2. Estatísticas de Categoria
    categoria_stats = qs_base.values('categoria__nome').annotate(total=Count('id')).order_by('-total')
    
    # 3. Evolução dos últimos 30 dias
    trinta_dias_atras = timezone.now() - timedelta(days=30)
    evolucao_stats = qs_base.filter(
        criado_em__gte=trinta_dias_atras
    ).annotate(
        data=TruncDate('criado_em')
    ).values('data').annotate(
        total=Count('id')
    ).order_by('data')

    # 4. Geocalização para Heatmap
    coordenadas = qs_base.exclude(
        latitude__isnull=True
    ).exclude(
        longitude__isnull=True
    ).values('latitude', 'longitude')

    # 5. KPIs (Indicadores Chave)
    stats = {
        'status_stats_json': json.dumps(list(status_stats)),
        'categoria_stats_json': json.dumps(list(categoria_stats)),
        'evolucao_stats_json': json.dumps([
            {'data': item['data'].strftime('%d/%m'), 'total': item['total']} 
            for item in evolucao_stats
        ]),
        'heatmap_data_json': json.dumps(list(coordenadas)),
        'total_relatos': qs_base.count(),
        'resolvidos': qs_base.filter(status_atual='resolvido').count(),
        'pendentes': qs_base.filter(status_atual='recebido').count(),
        'em_andamento': qs_base.filter(status_atual='em_progresso').count(),
        'bairros_disponiveis': RelatoZeladoria.objects.exclude(bairro__isnull=True).exclude(bairro='').values_list('bairro', flat=True).distinct().order_by('bairro'),
        'bairro_selecionado': bairro_selecionado or '',
    }
    
    return stats
