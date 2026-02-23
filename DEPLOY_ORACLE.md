# Guia de Deployment: Maricá Cidadão na Oracle Cloud (OCI)

Este guia cobre os passos necessários para colocar sua aplicação no ar assim que sua conta Oracle Cloud estiver liberada.

## 1. Criar a Instância (VM)
1. No console da OCI, vá em **Computação** -> **Instâncias** -> **Criar Instância**.
2. **Imagem**: Recomendo **Ubuntu 22.04** ou **Oracle Linux 8/9**.
3. **Forma**: Use a `VM.Standard.E4.Flex` (ou a `VM.Standard.A1.Flex` se quiser o "Always Free" ARM).
4. **Rede**: Certifique-se de atribuir um **endereço IP público**.
5. **Chaves SSH**: Baixe sua chave privada (.key) para acessar o servidor depois.

## 2. Configurar o Firewall (VCN Security List)
O Django e o Docker rodam na porta 8000 (ou 80/443 se usar Proxy).
1. Nas configurações da sua VCN -> **Default Security List**.
2. Adicione uma **Ingress Rule (Regra de Entrada)**:
   - **CIDR de Origem**: `0.0.0.0/0`
   - **Portas de Destino**: `8000, 80, 443`
   - **Protocolo**: TCP

## 3. Preparar o Servidor SSH
Acesse sua VM pelo terminal:
```bash
ssh -i sua_chave.key ubuntu@seu_ip_publico
```

## 4. Instalar Docker e Docker Compose
No terminal da VM:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```
*(Saia e entre novamente no SSH para aplicar as permissões do grupo Docker)*

## 5. Clonar e Rodar a Aplicação
```bash
# Clone seu repositório (ou envie os arquivos via SCP)
git clone <seu-repositorio>
cd app_marica_cidadao

# Criar o arquivo de ambiente
cp .env.example .env
nano .env  # Ajuste sua SECRET_KEY e ALLOWED_HOSTS (adicione o IP da VM)

# Rodar com Docker
docker-compose up --build -d
```

## 6. Comandos Úteis
- **Ver logs**: `docker-compose logs -f web`
- **Reiniciar**: `docker-compose restart`
- **Migrações**: `docker-compose exec web python manage.py migrate`
- **Criar Admin**: `docker-compose exec web python manage.py createsuperuser`

---
*Dica: Mantenha sua `SECRET_KEY` segura e nunca a compartilhe publicamente.*
