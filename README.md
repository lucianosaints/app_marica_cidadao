# 🏡 Maricá Cidadão - Zeladoria Urbana Inteligente

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Oracle](https://img.shields.io/badge/Oracle_Cloud-F80000?style=for-the-badge&logo=oracle&logoColor=white)

O **Maricá Cidadão** é uma plataforma moderna de Zeladoria Urbana que conecta os moradores de Maricá diretamente à prefeitura. O sistema permite reportar problemas (buracos, iluminação, lixo) com geolocalização automática e acompanhar a resolução através de uma linha do tempo transparente.

---

## ✨ Funcionalidades em Destaque

### 🛰️ Geolocalização Automática (GPS)
Implementamos uma captura proativa de GPS. Assim que o cidadão abre o formulário, o sistema sincroniza com os satélites e marca o local exato do problema no mapa sem necessidade de intervenção manual (via HTTPS).

### 📊 Painel Administrativo Premium
Interface administrativa baseada no **Jazzmin**, oferecendo uma experiência de gestão otimizada para os servidores da prefeitura, com dashboards, filtros avançados e logs de auditoria.

### 🛡️ Transparência Total
Cada mudança de status gera um registro histórico automático. O cidadão recebe atualizações em tempo real sobre o progresso do seu chamado.

---

## 🛠️ Stack Tecnológica

### Backend & API
- **Django 5.x**: Framework robusto para a lógica de negócio e Admin.
- **Django REST Framework**: API escalável para comunicação com o frontend.
- **Gunicorn & WhiteNoise**: Servidor de aplicação e gestão de arquivos estáticos em produção.
- **PostgreSQL**: Banco de dados relacional robusto para produção.

### Frontend
- **React 18**: Interface reativa e rápida para o cidadão.
- **Leaflet Maps**: Integração de mapas interativos para marcação de incidentes.
- **CSS3 Personalizado**: Design responsivo e focado em dispositivos móveis (Mobile-First).

### Infraestrutura & Deploy
- **Docker & Docker Compose**: Orquestração de containers para garantir que o app rode igual em qualquer lugar.
- **Oracle Cloud (OCI)**: Hospedagem de alta performance.
- **ngrok**: Túnel seguro HTTPS para habilitar geolocalização em navegadores modernos.

---

## 🚀 Como Executar o Projeto

### Modo Docker (Recomendado)
Para rodar o sistema completo em segundos:
```bash
docker-compose up --build -d
```
Acesse: `http://localhost:8000`

### Instalação Manual (Desenvolvimento)
1. Instale as dependências: `pip install -r requirements.txt`
2. Configure o `.env` (use o `.env.example` como base).
3. Rode as migrações: `python manage.py migrate`
4. Inicie o servidor: `python manage.py runserver`

---

## ☁️ Deploy na Oracle Cloud (OCI)

O projeto está configurado para deploy contínuo em instâncias Ubuntu na OCI.
1. Configure as **Ingress Rules** na VCN (Porta 8000).
2. Use o script `scripts/setup_oci.sh` para preparar o servidor.
3. Utilize o **ngrok** na VPS para ganhar o endereço HTTPS necessário para o GPS automático:
```bash
nohup ngrok http 8000 > /dev/null 2>&1 &
```

---

## 👥 Contribuição
Desenvolvido para a melhoria da gestão urbana de Maricá. Pull requests são bem-vindos!

---
*Prefeitura de Maricá - Inovação e Zeladoria.*
