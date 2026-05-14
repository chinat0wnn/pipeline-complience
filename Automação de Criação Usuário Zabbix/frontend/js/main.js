import { store } from './state/AppStore.js';
import { ApiService } from './services/ApiService.js';
import { FormController } from './ui/FormController.js';

document.addEventListener('DOMContentLoaded', () => {
    // Definindo a URL da API. No ambiente Kubernetes com Nginx Ingress, 
    // a API Flask é acessada no mesmo domínio usando o prefixo /api.
    // Localmente, você pode alterar para http://localhost:5000/api
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const API_BASE_URL = isLocalhost ? 'http://localhost:5000/api' : '/api';

    const apiService = new ApiService(API_BASE_URL);
    
    // Inicializa o controlador da interface
    new FormController(store, apiService);
    
    console.log("Portal de Provisionamento inicializado com sucesso.");
});
