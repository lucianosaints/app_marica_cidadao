# App Maricá Cidadão - Sistema de Zeladoria Urbana

Este é um sistema completo de Zeladoria Urbana desenvolvido para permitir que os cidadãos reportem problemas na cidade (como buracos na via, lâmpadas queimadas e focos de dengue) diretamente para a prefeitura, acompanhando a resolução em tempo real através de uma linha do tempo transparente.

## 🚀 Tecnologias Utilizadas

### Backend (API e Painel Administrativo)
- **Python 3.11**
- **Django 5.2** - Framework web principal.
- **Django REST Framework (DRF)** - Construção da API RESTful para comunicação com o aplicativo do cidadão.
- **Django REST Authtoken** - Sistema de autenticação seguro baseado em tokens para as requisições da API.
- **Django-CORS-Headers** - Gerenciamento de permissões CORS (Cross-Origin Resource Sharing) para permitir requisições do frontend.
- **Pillow** - Biblioteca para manipulação e salvamento das fotos enviadas pelos moradores.
- **SQLite3** - Banco de dados leve utilizado no ambiente de desenvolvimento.

### Frontend (Aplicação do Cidadão)
- **HTML5, CSS3, JavaScript (Vanilla e ES6+)**
- **React 18** (via CDN) - Criação de uma Single Page Application (SPA) para uma experiência de usuário fluida e reativa sem necessidade de recarregar a página.
- **Babel** (via CDN) - Transpilação de código JSX para JavaScript nativo interpretável pelos navegadores em tempo de execução.
- **Fetch API** - Comunicação assíncrona baseada em Promises com a API do Django.
- **HTML5 Geolocation API** - Captura automática das coordenadas de GPS (Latitude/Longitude) do dispositivo do usuário ao relatar um problema.

## 📋 Funcionalidades Em Destaque

**Para o Cidadão:**
- Cadastro e Autenticação (Login simulado com Gov.br).
- Relato de problemas urbanos com categoria, descrição, foto capturada pelo celular e coordenadas GPS automáticas.
- Dashboard "Meus Protocolos": Acompanhamento visual de todos os chamados abertos.
- Linha do Tempo: Visualização do histórico detalhado de mudanças de status do pedido (ex: Recebido, Em Análise, Equipe Despachada, Resolvido).

**Para a Prefeitura (Painel Admin Django):**
- Gerenciamento de Categorias de Problemas com estimativas de prazos.
- Visualização de todos os Relatos centralizados, com fotos e locais exatos.
- **Automação de Transparência:** Toda vez que um agente da prefeitura altera o status do relato de um cidadão no painel, o sistema cria automaticamente um novo registro no Histórico de Status daquele morador.

## ⚙️ Como Executar Localmente

**Pré-requisitos:** Python 3 instalado.

1. **Clone o repositório:**
   ```bash
   git clone [URL_DO_SEU_REPOSITORIO_AQUI]
   cd app_marica_cidadao
   ```

2. **Instale as dependências requeridas do backend:**
   ```bash
   pip install django djangorestframework django-cors-headers pillow
   ```

3. **Inicie o Servidor Backend (Django):**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
   ```

4. **Inicie o Frontend:**
   Basta abrir o arquivo `frontend_simples/index.html` diretamente no seu navegador, ou hospedá-mo em um servidor local estático simples (como a extensão Live Server do VSCode).

---
*Dúvidas ou sugestões? Envie um pull request!*
