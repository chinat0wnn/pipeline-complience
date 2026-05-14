# Automação de Provisionamento: Zabbix & Grafana

Bem-vindo ao repositório do **Portal de Provisionamento**, uma ferramenta desenvolvida para automatizar, simplificar e auditar a criação de usuários em ferramentas de monitoramento (Zabbix) baseada em perfis de acesso e "Squads".

---

## 🏗️ Arquitetura do Projeto

O projeto foi desenhado com foco em **escalabilidade**, **separação de responsabilidades (SRP)** e **alta performance**, sendo ideal para rodar nativamente em ambientes de contêineres (Docker / Kubernetes - AKS).

O sistema é composto por duas camadas principais:

### 1. Frontend (Interface de Usuário)
A interface foi construída seguindo rigorosas regras de engenharia front-end sem a dependência de frameworks pesados (React/Angular):
- **Vanilla JS (ES6 Modules)**: Todo o código Javascript está isolado em módulos.
- **Gerenciamento de Estado**: Utiliza um padrão `AppStore` centralizado para gerir *Loadings* e *Notificações*.
- **CSS Modular (BEM) & UI Premium**: Separação estrita de estilos com Design Tokens (`variables.css`). A interface conta com um design moderno em **Dark Mode**, efeitos de profundidade com **Glassmorphism**, micro-animações interativas e sistema de **Toast Notifications** flutuantes.
- **Web Server**: Projetado para ser servido por um contêiner **Nginx**, que não apenas entrega o conteúdo estático como atua de *Proxy Reverso* para o Backend (resolvendo problemas de CORS).

### 2. Backend (API Python)
A API atua como um "Wrapper" seguro em cima das chamadas JSON-RPC do Zabbix.
- **Framework Flask**: Leve, rápido e fácil de manter.
- **Padrão de Serviços**: A comunicação com as ferramentas externas fica isolada (ex: `zabbix_service.py`). Para adicionar o Grafana no futuro, bastará criar um `grafana_service.py`.
- **Stateless & Gunicorn**: Projetado para rodar de forma distribuída (Múltiplos workers Gunicorn) em contêineres Docker, sem armazenar sessão na memória do Python.

---

## ⚙️ Regras de Negócio: Tipos de Usuário e Squads

O portal não exige que o analista saiba os IDs de grupos (User Groups) do Zabbix de cabeça.
Ele funciona baseado na escolha de um **Tipo de Usuário (Role)** e um **Squad (Área)**.

A inteligência de mapeamento (tradução de "Squad Redes" para "IDs 11, 25 e 30") fica armazenada no Frontend (`frontend/js/ui/FormController.js`). O backend apenas recebe os números e orquestra a criação na ferramenta de destino.

> 📖 **Para mais detalhes sobre como criar ou modificar Squads, consulte o manual detalhado em:** `backend/SQUADS_DOCUMENTATION.md`

---

## 🚀 Como Executar o Projeto Localmente

Para rodar o projeto na sua máquina para fins de desenvolvimento ou testes, siga os passos abaixo:

### Pré-requisitos
- Python 3.10 ou superior
- Extensão "Live Server" no VS Code (para o Frontend)

### Passo 1: Configurar a API (Backend)
1. Abra um terminal e navegue até a pasta `backend`.
2. Renomeie (ou copie) o arquivo `.env.example` para `.env` e preencha as credenciais reais do seu servidor:
   ```env
   ZABBIX_URL=https://sua-url/zabbix/api_jsonrpc.php
   ZABBIX_USER=seu-usuario-api
   ZABBIX_PASS=sua-senha
   PORT=5000
   ```
3. Crie e ative o ambiente virtual Python:
   ```powershell
   python -m venv venv
   # No Windows:
   .\venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```
4. Instale as dependências:
   ```powershell
   pip install -r requirements.txt
   ```
5. Inicie a API:
   ```powershell
   python app.py
   ```
   *Você saberá que funcionou se acessar `http://localhost:5000/api/health` e receber um JSON com status "ok".*

### Passo 2: Iniciar a Interface (Frontend)
1. Navegue até a pasta `frontend`.
2. Clique com o botão direito no arquivo `index.html` e selecione **Open with Live Server**.
3. A página abrirá no navegador. Toda a comunicação com a porta `5000` (API) já está configurada automaticamente via CORS no ambiente local.

---

## 🐳 Deploy no Kubernetes (Azure AKS)

A infraestrutura foi preparada como "Container-Native".

1. **Geração das Imagens**:
   Existem dois `Dockerfiles` no projeto, um na raiz do `backend` (Python) e outro na raiz do `frontend` (Nginx). Você deverá construir essas imagens e enviá-las para o seu Container Registry (ex: ACR - Azure Container Registry).
   
2. **Manifestos do Kubernetes**:
   Na pasta `k8s/` estão os arquivos yaml para deploy:
   - `secrets.yaml`: Cadastre as credenciais do seu Zabbix convertidas em Base64 neste arquivo para manter a segurança no cluster.
   - `backend-deployment.yaml`: Responsável por subir a API na porta 5000.
   - `frontend-deployment.yaml`: Sobe o Nginx na porta 80. O arquivo `frontend/nginx.conf` já está programado para fazer o roteamento interno (Proxy Pass) das chamadas `/api/` para o serviço do Backend (DNS do Kubernetes).

---

**Tecnologias Utilizadas:**
*HTML5, Vanilla CSS (BEM), Vanilla JS (ES6), Python, Flask, Gunicorn, Nginx, Docker, Kubernetes.*
