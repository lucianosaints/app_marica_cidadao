import json
from pywebpush import webpush, WebPushException
from django.conf import settings
from .models import WebPushSubscription

def disparar_notificacao_push(user, title, message, url="/"):
    """
    Busca todas as inscrições ativas do usuário e envia a notificação via Push Service do Navegador.
    """
    subscriptions = WebPushSubscription.objects.filter(user=user)
    if not subscriptions.exists():
        return False
        
    vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', None)
    vapid_admin_email = getattr(settings, 'VAPID_ADMIN_EMAIL', 'mailto:admin@marica.rj.gov.br')
    
    if not vapid_private_key:
        print("Erro: VAPID_PRIVATE_KEY não configurada. Impossível enviar push.")
        return False

    payload = json.dumps({
        "title": title,
        "body": message,
        "url": url,
        "icon": "/logo192.png", # Adapte se necessário
        "badge": "/logo192.png" 
    })

    sucesso = False
    for sub in subscriptions:
        try:
            sub_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh,
                    "auth": sub.auth
                }
            }
            
            webpush(
                subscription_info=sub_info,
                data=payload,
                vapid_private_key=vapid_private_key,
                vapid_claims={"sub": vapid_admin_email}
            )
            sucesso = True
            print(f"Push enviado para o endpoint: {sub.endpoint[:30]}...")
            
        except WebPushException as ex:
            print("WebPush Erro:", repr(ex))
            # Se for um erro 410 (Gone), significa que o cidadão desinstalou o PWA ou removeu a permissão.
            if ex.response and ex.response.status_code in [404, 410]:
                print(f"Removendo inscrição inativa: {sub.endpoint[:30]}...")
                sub.delete()
        except Exception as e:
            print(f"Erro inesperado ao enviar push: {str(e)}")
            
    return sucesso
