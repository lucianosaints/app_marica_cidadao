import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_marica.settings')
django.setup()

from app_marica_cidadao.models import RelatoZeladoria, CategoriaProblema
from django.contrib.auth.models import User

# Garantindo que existe um Cidadão
cidadao, _ = User.objects.get_or_create(username='teste_cidadao_filtros')

# Pegando uma categoria aleatória ou criando
cat, _ = CategoriaProblema.objects.get_or_create(nome='Teste Geológico', defaults={'tempo_estimado_resolucao': 5})

bairros_teste = ['Itaipuaçu', 'Inoã', 'Ponta Negra']
coordenadas = {
    'Itaipuaçu': [(-22.9515, -42.9431), (-22.9600, -42.9300)],
    'Inoã': [(-22.9230, -42.9510), (-22.9150, -42.9480)],
    'Ponta Negra': [(-22.9560, -42.6950), (-22.9605, -42.6910)]
}

print("Criando relatos para os bairros: Inoã, Itaipuaçu e Ponta Negra...")

for bairro in bairros_teste:
    for lat, lng in coordenadas[bairro]:
        RelatoZeladoria.objects.create(
            cidadao=cidadao,
            categoria=cat,
            descricao=f"Teste sintético em {bairro}",
            endereco_aproximado=f"Rua Teste, {bairro}",
            bairro=bairro,
            latitude=lat,
            longitude=lng,
            status_atual=random.choice(['recebido', 'resolvido', 'em_progresso'])
        )

print("Relatos criados com sucesso!")
print("Registros totais no banco:", RelatoZeladoria.objects.count())
