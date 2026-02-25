from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import HistoricoStatus

@receiver(post_save, sender=HistoricoStatus)
def notificar_mudanca_status(sender, instance, created, **kwargs):
    """
    Sempre que um novo histórico de status é criado, 
    uma notificação simulada é enviada ao cidadão.
    """
    if created:
        relato = instance.relato
        cidadao = relato.cidadao
        # Tenta pegar o telefone do PerfilCidadao
        telefone = getattr(cidadao.perfil, 'telefone', 'Não cadastrado')
        
        status_msg = instance.get_status_display()
        
        print(f"\n--- [SIMULAÇÃO WHATSAPP] ---")
        print(f"Para: {telefone}")
        print(f"Mensagem: Olá {cidadao.first_name or cidadao.username}, o status do seu relato #{relato.id} ({relato.categoria.nome}) mudou para: {status_msg}.")
        if instance.observacao_prefeitura:
            print(f"Observação da Prefeitura: {instance.observacao_prefeitura}")
        print(f"--- FIM DA SIMULAÇÃO ---\n")
