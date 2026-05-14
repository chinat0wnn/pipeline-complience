#!/bin/bash

# Substitua 'SEU_TOKEN_AQUI' pelo token que o Grafana gerou quando você clicou em "Add token"
TOKEN="seu_token_grafana_aqui"
URL="https://noc.dataside.com.br/api"

echo "--- Testando Identidade ---"
curl -s -L -H "Authorization: Bearer $TOKEN" "$URL/user" | jq .

echo -e "\n--- Tentando Criar Usuário (Admin Global) ---"
curl -s -L -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"User Teste","email":"teste@dataside.com.br","login":"user.teste","password":"password123"}' \
  "$URL/admin/users" | jq .
