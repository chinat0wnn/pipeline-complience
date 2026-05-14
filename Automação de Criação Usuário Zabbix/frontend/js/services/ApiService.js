export class ApiService {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    async provisionUser(userData) {
        try {
            // Em produção/AKS a requisição vai para a rota /api (proxy do nginx)
            const response = await fetch(`${this.baseUrl}/provision`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();

            if (!response.ok || (data.grafana && data.grafana.status === 'error') || (data.zabbix && data.zabbix.status === 'error')) {
                let errorMsg = data.error;
                if (!errorMsg && data.grafana && data.grafana.status === 'error') {
                    errorMsg = `Grafana: ${data.grafana.message}`;
                }
                if (!errorMsg && data.zabbix && data.zabbix.status === 'error') {
                    errorMsg = `Zabbix: ${data.zabbix.message}`;
                }
                throw new Error(errorMsg || 'Erro desconhecido ao provisionar usuário.');
            }

            return data;
        } catch (error) {
            throw error;
        }
    }

    async getZabbixGroups() {
        try {
            const response = await fetch(`${this.baseUrl}/zabbix/groups`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Erro ao buscar grupos do Zabbix.');
            }

            return data.groups;
        } catch (error) {
            throw error;
        }
    }
}
