from django.db import models
from django.contrib.auth.models import User

class CategoriaProblema(models.Model):
    """
    Categorias dos problemas que o cidadão pode relatar.
    Ex: 'Buraco na via', 'Lâmpada Queimada', 'Foco de Dengue'.
    """
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    icone = models.ImageField(upload_to='icones_categorias/', blank=True, null=True)
    emoji = models.CharField(max_length=10, blank=True, null=True, help_text="Emoji para exibição no formulário")
    tempo_estimado_resolucao = models.IntegerField(
        help_text="Tempo estimado para resolução em dias"
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria de Problema"
        verbose_name_plural = "Categorias de Problemas"


class RelatoZeladoria(models.Model):
    """
    O ticket principal criado pelo cidadão.
    """
    STATUS_CHOICES = [
        ('recebido', 'Recebido'),
        ('em_analise', 'Em Análise'),
        ('equipe_despachada', 'Equipe no Local'),
        ('resolvido', 'Resolvido'),
        ('rejeitado', 'Rejeitado / Improcedente'),
    ]

    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
    ]

    cidadao = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relatos')
    categoria = models.ForeignKey(CategoriaProblema, on_delete=models.PROTECT)
    
    # Dados do problema
    descricao = models.TextField(help_text="Descrição detalhada do cidadão")
    foto_problema = models.ImageField(upload_to='relatos_cidadao/', blank=True, null=True, help_text="Foto do problema (obrigatório)")
    
    # Geolocalização
    latitude = models.FloatField(help_text="Latitude", null=True, blank=True)
    longitude = models.FloatField(help_text="Longitude", null=True, blank=True)
    endereco_aproximado = models.CharField(max_length=255, blank=True, null=True)
    bairro = models.CharField(max_length=150, blank=True, null=True, help_text="Bairro onde o problema ocorreu")
    
    # Propriedade Privada
    e_propriedade_privada = models.BooleanField(default=False, help_text="O problema é em uma propriedade privada?")
    comprovante_titularidade = models.FileField(upload_to='comprovantes_relatos/', blank=True, null=True, help_text="Necessário se for propriedade privada")
    aceite_termo_ambiental = models.BooleanField(default=False, help_text="Ciente da compensação ambiental conforme Lei 2367/2011")
    
    # Controle de estado e IA
    status_atual = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recebido')
    prioridade = models.CharField(max_length=20, choices=PRIORIDADE_CHOICES, default='baixa', help_text="Estimada pela IA ou servidora")
    justificativa_ia = models.TextField(blank=True, null=True, help_text="Explicação técnica da IA")
    
    # Feedback do Cidadão (Pós-Resolução)
    avaliacao = models.IntegerField(null=True, blank=True, help_text="Avaliação de 1 a 5 estrelas")
    comentario_cidadao = models.TextField(null=True, blank=True, help_text="Comentário do cidadão sobre a resolução")

    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Protocolo #{self.id} - {self.categoria.nome}"

    class Meta:
        verbose_name = "Relato de Zeladoria"
        verbose_name_plural = "Relatos de Zeladoria"
        ordering = ['-criado_add'] if hasattr(models, 'criado_add') else ['-criado_em']


class HistoricoStatus(models.Model):
    """
    Garante a transparência. Cada vez que o status do relato muda,
    um registro é criado aqui. O React pode ler isso para montar a 'linha do tempo' do chamado.
    """
    relato = models.ForeignKey(RelatoZeladoria, on_delete=models.CASCADE, related_name='historico')
    status = models.CharField(max_length=20, choices=RelatoZeladoria.STATUS_CHOICES)
    observacao_prefeitura = models.TextField(
        blank=True, 
        help_text="Mensagem da prefeitura para o cidadão (ex: 'Buraco tapado com sucesso')"
    )
    foto_resolucao = models.ImageField(upload_to='resolucoes_prefeitura/', blank=True, null=True)
    
    # Quem atualizou e quando
    atualizado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Servidor da prefeitura que atualizou o status"
    )
    data_atualizacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_atualizacao']
        verbose_name = "Histórico de Status"
        verbose_name_plural = "Históricos de Status"

    def __str__(self):
        return f"Atualização #{self.id} para Relato #{self.relato.id}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Envia a notificação Push quando um novo histórico é criado (status alterado no banco)
            try:
                from .webpush_service import disparar_notificacao_push
                from .models import RelatoZeladoria
                
                status_legivel = dict(RelatoZeladoria.STATUS_CHOICES).get(self.status, self.status)
                titulo = f"Maricá Cidadão - Atualização"
                mensagem = f"O status do seu chamado '{self.relato.categoria.nome}' mudou para: {status_legivel}."
                
                if self.observacao_prefeitura:
                    mensagem += f"\nObs: {self.observacao_prefeitura}"
                    
                disparar_notificacao_push(
                    user=self.relato.cidadao,
                    title=titulo,
                    message=mensagem,
                    url="/"
                )
            except Exception as e:
                print(f"Aviso: Falha ao enviar WebPush automático: {str(e)}")



class PerfilCidadao(models.Model):
    """
    Extensão do modelo User para armazenar dados adicionais do cidadão.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    cpf = models.CharField(max_length=14, unique=True, help_text="CPF formatado (ex: 000.000.000-00)")
    telefone = models.CharField(max_length=20, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    
    # Endereço
    cep = models.CharField(max_length=9, blank=True, null=True)
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, default='Maricá')
    
    # Documentação opcional
    comprovante_titularidade = models.FileField(
        upload_to='comprovantes_titularidade/', 
        blank=True, 
        null=True,
        help_text="Opcional: Comprovante de titularidade de imóvel caso a ação seja em local privado"
    )

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.cpf})"

    class Meta:
        verbose_name = "Perfil do Cidadão"
        verbose_name_plural = "Perfis dos Cidadãos"


class WebPushSubscription(models.Model):
    """
    Armazena as inscrições dos dispositivos dos cidadãos para receber push notifications.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webpush_subscriptions')
    endpoint = models.URLField(max_length=500, unique=True, help_text="URL gerada pelo serviço de push do navegador")
    p256dh = models.CharField(max_length=200, help_text="Chave pública do dispositivo (ECDH)")
    auth = models.CharField(max_length=200, help_text="Segredo de autenticação do dispositivo")
    
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Inscrição WebPush"
        verbose_name_plural = "Inscrições WebPush"

    def __str__(self):
        return f"Push endpoint para {self.user.username}"
