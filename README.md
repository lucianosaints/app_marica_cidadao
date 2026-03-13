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

### 🤖 Inteligência Artificial (Gemini 1.5 Flash)
O sistema utiliza IA para analisar as fotos dos problemas em tempo real. A IA sugere automaticamente a categoria do incidente e define a prioridade (Alta, Média, Baixa) com base na gravidade visual, agilizando a triagem da prefeitura.

### 📱 PWA & Funcionamento Offline
O aplicativo é um **PWA (Progressive Web App)**, permitindo a instalação no celular como um app nativo. Conta com persistência via **IndexedDB**, permitindo que o cidadão registre problemas mesmo sem internet; o envio é sincronizado automaticamente assim que a conexão retorna.

### 🔔 Notificações WebPush
Integração com o serviço de **WebPush** do navegador para enviar notificações em tempo real diretamente para o dispositivo do cidadão quando houver atualizações nos seus chamados.

### 📊 Painel Administrativo Premium & Relatórios
Interface administrativa baseada no **Jazzmin** com dashboards interativos, heatmap de incidentes e geração de **relatórios gerenciais em PDF** para suporte à tomada de decisão pública.

---

## 🛠️ Stack Tecnológica

### Backend & API
- **Django 5.x**: Core do sistema e lógica de negócio.
- **Django REST Framework**: API para comunicação frontend-backend.
- **Google Generative AI**: Integração com Gemini para análise de imagens.
- **FPDF2**: Geração de relatórios PDF profissionais.
- **PyWebPush**: Motor de notificações push.
- **Gunicorn & WhiteNoise**: Servidor de aplicação e gestão de estáticos.
- **PostgreSQL**: Banco de dados relacional.

### Frontend (PWA)
- **Vanilla JS & React 18 (Cidadão)**: Interface reativa e Mobile-First.
- **Leaflet Maps**: Mapas interativos e georreferenciamento.
- **IndexedDB**: Armazenamento local para modo offline.
- **Service Workers**: Cache de ativos e recepção de notificações push.

### Infraestrutura & Deploy
- **Docker & Docker Compose**: Padronização do ambiente de execução.
- **Oracle Cloud (OCI)**: Hospedagem escalável.
- **ngrok**: Túnel HTTPS para geolocalização segura em desenvolvimento.

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
2. Utilize o **ngrok** na VPS para ganhar o endereço HTTPS necessário para o GPS automático e WebPush:
```bash
nohup ngrok http 8000 > /dev/null 2>&1 &
```

---

## 👥 Contribuição
Desenvolvido para a melhoria da gestão urbana de Maricá. Pull requests são bem-vindos!

---
*Prefeitura de Maricá - Inovação e Zeladoria.*
