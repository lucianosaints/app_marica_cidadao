from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import HistoricoStatus

@receiver(post_save, sender=HistoricoStatus)
def notificar_mudanca_status(sender, instance, created, **kwargs):
    """
    Sempre que um novo histórico de status é criado:
    1. Atualiza o status_atual do RelatoZeladoria vinculado.
    2. Envia uma notificação simulada ao cidadão.
    """
    if created:
        relato = instance.relato
        
        # 1. Sincronização de Status (Garante que o frontend veja a mudança)
        if relato.status_atual != instance.status:
            relato.status_atual = instance.status
            relato.save(update_fields=['status_atual', 'atualizado_em'])
            print(f"INFO: Status do Relato #{relato.id} sincronizado para: {instance.status}")

        cidadao = relato.cidadao
        # Tenta pegar o telefone do PerfilCidadao de forma segura
        perfil = getattr(cidadao, 'perfil', None)
        telefone = getattr(perfil, 'telefone', 'Não cadastrado') if perfil else 'Não cadastrado'
        
        status_msg = instance.get_status_display()
        
        print(f"\n--- [SIMULAÇÃO WHATSAPP] ---")
        print(f"Para: {telefone}")
        print(f"Mensagem: Olá {cidadao.first_name or cidadao.username}, o status do seu relato #{relato.id} ({relato.categoria.nome}) mudou para: {status_msg}.")
        if instance.observacao_prefeitura:
            print(f"Observação da Prefeitura: {instance.observacao_prefeitura}")
        print(f"--- FIM DA SIMULAÇÃO ---\n")
