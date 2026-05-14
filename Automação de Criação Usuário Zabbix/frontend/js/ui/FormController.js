export class FormController {
    constructor(store, apiService) {
        this.store = store;
        this.apiService = apiService;

        // Elements
        this.form = document.getElementById('provision-form');
        this.toast = document.getElementById('toast');
        this.submitBtn = document.getElementById('submit-btn');
        this.spinner = this.submitBtn.querySelector('.btn__spinner');

        // Bindings
        this.handleSubmit = this.handleSubmit.bind(this);
        this.render = this.render.bind(this);

        // Subscriptions & Listeners
        this.store.subscribe(this.render);
        this.form.addEventListener('submit', this.handleSubmit);

        // Init
        this.loadGroups();
    }

    async loadGroups() {
        const groupsSelect = document.getElementById('groups');
        try {
            const groups = await this.apiService.getZabbixGroups();
            groupsSelect.innerHTML = ''; // Clear loading text
            groups.forEach(group => {
                const option = document.createElement('option');
                option.value = group.usrgrpid;
                option.textContent = group.name;
                groupsSelect.appendChild(option);
            });
        } catch (error) {
            groupsSelect.innerHTML = '<option value="" disabled>Erro ao carregar grupos</option>';
            this.store.setNotification('error', 'Não foi possível carregar os grupos do Zabbix: ' + error.message);
        }
    }

    async handleSubmit(event) {
        event.preventDefault();

        this.store.clearNotification();
        this.store.setLoading(true);

        const formData = new FormData(this.form);

        // Capturar targets (checkboxes) - Forçado para zabbix pois Grafana foi pausado
        let targets = formData.getAll('targets');
        if (targets.length === 0) {
            targets = ['zabbix'];
        }

        // Mapeamento de Squads para IDs de Grupos no Zabbix
        const SQUAD_GROUPS_MAP = {
            "infra": [28, 13, 15],     // Ex: Enabled debug mode (11) + Infra (15)
            "db": [28, 13, 14],    // Ex: Enabled debug mode (11) + DB (16)
            "dev": [28, 13, 21]            // Ex: Leitura (14)
        };

        const squadId = formData.get('squad');
        const squadGroups = SQUAD_GROUPS_MAP[squadId] || [];

        // Capturar múltiplos grupos adicionais selecionados
        const extraGroups = formData.getAll('groups').map(id => parseInt(id, 10));

        // Mesclar garantindo IDs únicos (Sem repetição)
        const combinedGroups = [...new Set([...squadGroups, ...extraGroups])];

        if (combinedGroups.length === 0) {
            this.store.setNotification('error', 'É necessário selecionar uma Squad ou um Grupo.');
            this.store.setLoading(false);
            return;
        }

        const payload = {
            alias: formData.get('alias'),
            email: formData.get('email'),
            name: formData.get('name'),
            surname: formData.get('surname'),
            roleid: parseInt(formData.get('role'), 10),
            usrgrpids: combinedGroups,
            targets: targets
        };

        try {
            const result = await this.apiService.provisionUser(payload);
            let successMessage = `Sucesso! `;
            if (result.zabbix && result.zabbix.status === 'success') {
                successMessage += `Zabbix (ID: ${result.zabbix.userid}). `;
            }
            if (result.grafana && result.grafana.status === 'success') {
                successMessage += `Grafana criado. Senha: ${result.grafana.initial_password}`;
            }
            this.store.setNotification('success', successMessage);
            this.form.reset();
        } catch (error) {
            this.store.setNotification('error', error.message);
        } finally {
            this.store.setLoading(false);
        }
    }

    render(state) {
        // Handle Loading State
        if (state.isLoading) {
            this.submitBtn.disabled = true;
            this.spinner.classList.remove('hidden');
        } else {
            this.submitBtn.disabled = false;
            this.spinner.classList.add('hidden');
        }

        // Handle Notifications
        if (state.notification) {
            this.toast.textContent = state.notification.message;
            this.toast.className = `toast toast--${state.notification.type} show`;
            
            // Auto hide after 5 seconds
            if (this.toastTimeout) {
                clearTimeout(this.toastTimeout);
            }
            this.toastTimeout = setTimeout(() => {
                this.store.clearNotification();
            }, 5000);
        } else {
            this.toast.className = 'toast';
        }
    }
}
