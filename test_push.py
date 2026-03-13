import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_marica.settings')
django.setup()

from app_marica_cidadao.models import WebPushSubscription
from app_marica_cidadao.webpush_service import disparar_notificacao_push

sub = WebPushSubscription.objects.last()
if sub:
    print(f"Testando push para usuário: {sub.user.username} (Endpoint: {sub.endpoint[:30]}...)")
    try:
        sucesso = disparar_notificacao_push(sub.user, "Teste Técnico 🚀", "Verificando se o push de teste chega na sua tela!", "/")
        print("A API de Push retornou sucesso:", sucesso)
    except Exception as e:
        import traceback
        traceback.print_exc()
else:
    print("Nenhuma subscription encontrada no banco.")
