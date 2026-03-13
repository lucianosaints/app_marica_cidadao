import os
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

def generate_vapid_keys():
    # Gerar a chave privada EC P-256
    private_key = ec.generate_private_key(ec.SECP256R1())

    # Converter para formato JWK / Base64Url
    private_numbers = private_key.private_numbers()
    public_numbers = private_key.public_key().public_numbers()

    # Formatar os números para bytes e aplicar base64url sem padding
    def b64url_encode(data):
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

    def int_to_bytes(x):
        return x.to_bytes((x.bit_length() + 7) // 8, byteorder='big')

    d = b64url_encode(int_to_bytes(private_numbers.private_value))
    x = b64url_encode(int_to_bytes(public_numbers.x))
    y = b64url_encode(int_to_bytes(public_numbers.y))

    # Formatar a chave pública segundo a especificação VAPID (0x04 + X + Y)
    pub_bytes = b'\x04' + int_to_bytes(public_numbers.x) + int_to_bytes(public_numbers.y)
    vapid_public_key = b64url_encode(pub_bytes)
    
    # Montar a chave privada compacta esperada por algumas libs ou manter apenas o D
    vapid_private_key = d
    
    print("VAPID_PUBLIC_KEY=" + vapid_public_key)
    print("VAPID_PRIVATE_KEY=" + vapid_private_key)
    
    # Adicionar ao .env
    env_path = os.path.join(os.getcwd(), 'projeto_marica', '.env')
    if not os.path.exists(env_path):
        env_path = os.path.join(os.getcwd(), '.env')
        
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            content = f.read()
        
        if 'VAPID_PUBLIC_KEY' not in content:
            with open(env_path, 'a') as f:
                f.write(f"\n# Config WebPush\nVAPID_PUBLIC_KEY={vapid_public_key}\nVAPID_PRIVATE_KEY={vapid_private_key}\nVAPID_ADMIN_EMAIL=mailto:admin@marica.rj.gov.br\n")
            print(f"Chaves salvas com sucesso em: {env_path}")
        else:
            print("Chaves VAPID já existem no .env")
    else:
        print(f"Arquivo .env não encontrado. Crie manualmente as chaves.")

if __name__ == "__main__":
    generate_vapid_keys()
