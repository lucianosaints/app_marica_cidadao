from rest_framework import serializers

from .models import CategoriaProblema, RelatoZeladoria, HistoricoStatus

class HistoricoStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoStatus
        fields = ['status', 'get_status_display', 'observacao_prefeitura', 'foto_resolucao', 'data_atualizacao']
    
    get_status_display = serializers.CharField(source='get_status_display', read_only=True)

class RelatoZeladoriaSerializer(serializers.ModelSerializer):
    # Traz o histórico aninhado (apenas leitura para o cidadão)
    historico = HistoricoStatusSerializer(many=True, read_only=True)
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    status_display = serializers.CharField(source='get_status_atual_display', read_only=True)

    class Meta:
        model = RelatoZeladoria
        fields = [
            'id', 'categoria', 'categoria_nome', 'descricao', 'foto_problema',
            'endereco_aproximado', 'status_atual', 'status_display', 'criado_em',
            'historico', 'latitude', 'longitude'
        ]
        # O cidadão não pode alterar o status ou a data de criação manualmente
        read_only_fields = ['status_atual', 'criado_em']

    def create(self, validated_data):
        # Pega o usuário logado automaticamente da requisição
        validated_data['cidadao'] = self.context['request'].user
        
        relato = super().create(validated_data)
        
        # Cria a primeira entrada de histórico automaticamente
        HistoricoStatus.objects.create(
            relato=relato,
            status=relato.status_atual,
            observacao_prefeitura="Relato recebido pelo sistema. Aguardando triagem.",
            atualizado_por=None # Sistema gerou
        )
        
        return relato