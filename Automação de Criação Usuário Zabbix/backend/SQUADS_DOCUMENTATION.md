# Documentação Técnica: Lógica de Provisionamento Baseado em Squads

Este documento explica detalhadamente como funciona a arquitetura de **"Tipos de Usuário (Roles)"** e **"Squads (Grupos)"** dentro da ferramenta de provisionamento do Zabbix. O objetivo é permitir que qualquer desenvolvedor ou administrador compreenda e consiga dar manutenção no mapeamento de acessos.

---

## 1. O Problema
No Zabbix, para dar a permissão correta a um usuário de uma determinada área (ex: Banco de Dados), o administrador precisava adicionar este usuário a 3 ou 4 *User Groups* (`usrgrpids`) diferentes manualmente (ex: *Enabled debug mode*, *Clientes*, *Dataside/Banco*).

## 2. A Solução (Mapeamento Frontend -> Backend)
Criamos uma inteligência na camada visual (Frontend) que traduz o nome amigável da área ("Squad Banco de Dados") em um array contendo todos os IDs numéricos que o Zabbix exige.

### O Fluxo da Requisição
1. **O Usuário seleciona o Squad na Interface (HTML)**
2. **O JavaScript intercepta a seleção e traduz os IDs**
3. **O Backend (Python) recebe a lista de IDs e os envia para a API do Zabbix**

---

## 3. Como configurar ou adicionar um novo Squad?

A manutenção dos Squads é feita **exclusivamente na camada Frontend**, especificamente nestes dois arquivos:

### Passo A: Atualizar a Interface (`frontend/index.html`)
Você precisa adicionar uma nova `<option>` dentro do `select` que tem o `id="squad"`.
Exemplo:
```html
<select id="squad" name="squad" class="form__input" required>
    <!-- Outras opções ... -->
    <option value="redes">Squad de Redes</option>
</select>
```
*A propriedade `value="redes"` é a chave de identificação única que o Javascript usará.*

### Passo B: Atualizar o Mapeamento (`frontend/js/ui/FormController.js`)
Neste arquivo, existe uma constante chamada `SQUAD_GROUPS_MAP`. Você precisa associar a chave criada no HTML (`redes`) com os **IDs Reais dos Grupos no Zabbix**.

Para descobrir o ID de um grupo no Zabbix, acesse o Zabbix > Administração > Grupos de Usuário e observe o número na URL (ex: `usrgrpid=25`).

Exemplo de adição no Javascript:
```javascript
const SQUAD_GROUPS_MAP = {
    "infra": [11, 15],
    "db": [11, 50, 99],
    "redes": [11, 25, 30] // <-- Novo Squad adicionado
};
```

---

## 4. O Papel do Backend (`app.py` e `zabbix_service.py`)

A API em Python foi desenhada para ser **agnóstica**. Ela não sabe o que é um "Squad". 
Ela apenas recebe dois campos fundamentais enviados pelo Frontend e os repassa para o Zabbix através do método `user.create`:

- `roleid`: O tipo do usuário (1 = User, 2 = Admin, 3 = Super Admin). O Zabbix usa isso para liberar a interface web.
- `usrgrpids`: A lista de grupos que o Javascript empacotou (ex: `[11, 25, 30]`). O Zabbix usa isso para liberar o acesso aos hosts e alertas.

**Tratamento no Python:**
```python
# Em zabbix_service.py
usrgrps = [{"usrgrpid": str(grp_id)} for grp_id in usrgrpids]

params = {
    "alias": alias,
    "roleid": str(roleid),
    "usrgrps": usrgrps, # Transforma [11, 25] em [{"usrgrpid": "11"}, {"usrgrpid": "25"}]
    # ...
}
```

Dessa forma, o Backend não precisa ser modificado a cada nova área ou Squad criado na empresa. Toda a configuração fica no Frontend, deixando a API leve e estável.
