# Pipeline de Compliance as Code para Docker 🔒🐳

Este repositório fornece uma infraestrutura pronta para garantir a segurança da sua aplicação Dockerizada desde o momento do push de código, operando como um verdadeiro "Gatekeeper" (Portão de Segurança).

Utiliza **GitHub Actions**, **Trivy** (para scan de imagem) e **Gitleaks** (para scan de segredos).

## 🚀 Como Integrar o seu Projeto

1.  **Clone este repositório** e adicione os arquivos do seu projeto.
2.  **Substitua o arquivo `Dockerfile`** pelo Dockerfile da sua aplicação.
3.  Faça o **commit e o push** das mudanças para o GitHub.
4.  O GitHub Actions rodará automaticamente a pipeline e validará a segurança do seu código e da sua imagem Docker.

## ⚙️ Regras de Bloqueio e Thresholds de Segurança

Este projeto adota a estratégia de "Compliance as Code", onde limites de segurança são impostos diretamente no processo de CI.

### 🔴 Bloqueio Imediato (A Pipeline Falhará)
A pipeline será **cancelada** (Exit Code 1) impedindo o deploy ou o merge do código nos seguintes cenários:

1.  **Vazamento de Segredos**: O `Gitleaks` encontrou chaves de API, tokens da AWS, senhas ou arquivos `.env` commitados indevidamente no histórico.
2.  **Vulnerabilidades Críticas e Altas (HIGH, CRITICAL)**: A imagem base do seu Dockerfile ou os pacotes instalados possuem falhas de segurança graves conhecidas (CVEs).
3.  **Configurações Inseguras (Misconfigurations)**: O Dockerfile foi construído com más práticas graves (ex: rodar como usuário `root` indevidamente, ou vazar variáveis de ambiente críticas).

### 🟡 Avisos e Relatórios (A Pipeline Passará)
Para não bloquear o desenvolvimento ágil, as seguintes categorias gerarão relatórios e avisos, mas **não falharão** a pipeline:

1.  **Vulnerabilidades Médias e Baixas (MEDIUM, LOW)**: O `Trivy` identificará essas falhas e gerará um relatório detalhado.
2.  **Integração SARIF**: Um relatório completo de segurança no formato **SARIF** será enviado diretamente para a aba **Security > Code Scanning** do GitHub do seu repositório. Isso permite que você visualize e gerencie a dívida técnica de segurança ao longo do tempo.

## 🛠️ Arquitetura da Pipeline

O arquivo `.github/workflows/compliance.yml` executa as seguintes etapas:
1.  **Checkout**: Faz o pull completo do histórico para análise de commits antigos.
2.  **Gitleaks**: Rastreia segredos no histórico.
3.  **Docker Build**: Constrói a imagem localmente (sem fazer push).
4.  **Trivy (Scan Passivo)**: Procura vulnerabilidades (MEDIUM/LOW) e envia o log (SARIF) para a aba Security.
5.  **Trivy (Scan Ativo)**: Analisa a imagem buscando severidades HIGH e CRITICAL. Caso encontre, falha a esteira.

## 📝 Ignorando Falsos Positivos

Se o Gitleaks bloquear um segredo que seja falso (como uma chave de teste em arquivos de mock), você pode atualizar o arquivo `.gitleaks.toml` para ignorar caminhos específicos ou criar *allowlists*.
