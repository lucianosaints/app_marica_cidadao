from rest_framework import serializers

from django.contrib.auth.models import User
from .models import CategoriaProblema, RelatoZeladoria, HistoricoStatus, PerfilCidadao
from django.db import transaction

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    # Novos campos do perfil (write_only pois não existem no modelo User diretamente)
    cpf = serializers.CharField(max_length=14, write_only=True)
    telefone = serializers.CharField(max_length=20, required=False, allow_blank=True, write_only=True)
    data_nascimento = serializers.DateField(required=False, allow_null=True, write_only=True)
    cep = serializers.CharField(max_length=9, required=False, allow_blank=True, write_only=True)
    logradouro = serializers.CharField(max_length=255, required=False, allow_blank=True, write_only=True)
    numero = serializers.CharField(max_length=20, required=False, allow_blank=True, write_only=True)
    bairro = serializers.CharField(max_length=100, required=False, allow_blank=True, write_only=True)
    cidade = serializers.CharField(max_length=100, default='Maricá', write_only=True)
    comprovante_titularidade = serializers.FileField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'cpf', 'telefone', 'data_nascimento', 'cep', 'logradouro', 
            'numero', 'bairro', 'cidade', 'comprovante_titularidade'
        ]

    def validate_cpf(self, value):
        if PerfilCidadao.objects.filter(cpf=value).exists():
            raise serializers.ValidationError("Este CPF já está cadastrado.")
        return value

    def create(self, validated_data):
        # Extrair dados do perfil
        perfil_data = {
            'cpf': validated_data.pop('cpf'),
            'telefone': validated_data.pop('telefone', ''),
            'data_nascimento': validated_data.pop('data_nascimento', None),
            'cep': validated_data.pop('cep', ''),
            'logradouro': validated_data.pop('logradouro', ''),
            'numero': validated_data.pop('numero', ''),
            'bairro': validated_data.pop('bairro', ''),
            'cidade': validated_data.pop('cidade', 'Maricá'),
            'comprovante_titularidade': validated_data.pop('comprovante_titularidade', None),
        }

        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data.get('email', ''),
                password=validated_data['password'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', '')
            )
            
            PerfilCidadao.objects.create(user=user, **perfil_data)
            
        return user


class CategoriaProblemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProblema
        fields = ['id', 'nome', 'descricao', 'emoji']


class HistoricoStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoStatus
        fields = ['status', 'get_status_display', 'observacao_prefeitura', 'foto_resolucao', 'data_atualizacao']
    
    get_status_display = serializers.CharField(read_only=True)

class RelatoZeladoriaSerializer(serializers.ModelSerializer):
    # Traz o histórico aninhado (apenas leitura para o cidadão)
    historico = HistoricoStatusSerializer(many=True, read_only=True)
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    categoria_emoji = serializers.CharField(source='categoria.emoji', read_only=True)
    status_display = serializers.CharField(source='get_status_atual_display', read_only=True)

    class Meta:
        model = RelatoZeladoria
        fields = [
            'id', 'categoria', 'categoria_nome', 'categoria_emoji', 'descricao', 'foto_problema',
            'endereco_aproximado', 'status_atual', 'status_display', 'criado_em',
            'historico', 'latitude', 'longitude', 'avaliacao', 'comentario_cidadao',
            'e_propriedade_privada', 'comprovante_titularidade'
        ]
        # O cidadão não pode alterar o status ou a data de criação manualmente
        read_only_fields = ['status_atual', 'criado_em']

    def validate(self, data):
        """
        Validações customizadas para o Relato.
        """
        # Se estiver tentando enviar avaliação/comentário
        if 'avaliacao' in data or 'comentario_cidadao' in data:
            # No caso de criação, obviamente não pode ter avaliação
            if not self.instance:
                raise serializers.ValidationError(
                    {"avaliacao": "Você não pode avaliar um chamado que ainda não foi criado."}
                )
            
            # No caso de atualização, só pode se o status for resolvido
            if self.instance.status_atual != 'resolvido':
                raise serializers.ValidationError(
                    {"avaliacao": "A avaliação só é permitida após a resolução do chamado pela prefeitura."}
                )
        
        return data

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