# =========================================================================
# DOCKERFILE TEMPLATE (Substitua pelo Dockerfile do seu projeto)
# =========================================================================
# Este é um exemplo básico para testar a pipeline de segurança.
#
# Para testar o bloqueio da pipeline (HIGH/CRITICAL):
# Descomente a linha abaixo (node:14) que possui vulnerabilidades conhecidas:
# FROM node:14-alpine
#
# Para um build seguro (Aprovado na pipeline):
FROM node:20-alpine

# Define o diretório de trabalho
WORKDIR /app

# (Opcional) Teste de Gitleaks: Evite colocar senhas aqui ou no código!
# ENV AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE" # <-- Isso faria a pipeline falhar!

# Adicione o código do seu projeto aqui
# COPY . .
# RUN npm install
# EXPOSE 3000
# CMD ["npm", "start"]

# Boa Prática (Misconfig): Rodar como usuário não-root (O Trivy valida isso)
# Omitir isso em algumas imagens base pode gerar avisos no Trivy.
USER node

# Apenas um comando de exemplo para manter o container vivo caso executado
CMD ["echo", "Container base criado com sucesso. Substitua pelo seu código!"]
