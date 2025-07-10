import api from './api';

class PlaidService {
  // Crear link token para conectar con Plaid
  async createLinkToken() {
    try {
      const response = await api.post('/plaid/create-link-token');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Crear public token (para sandbox/testing)
  async createPublicToken() {
    try {
      const response = await api.post('/plaid/create-public-token');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Intercambiar public token por access token
  async exchangePublicToken(publicToken) {
    try {
      const response = await api.post('/plaid/exchange-public-token', {
        public_token: publicToken
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Desconectar de Plaid
  async disconnect() {
    try {
      const response = await api.post('/plaid/disconnect');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Verificar estado de conexión con Plaid
  async getStatus() {
    try {
      const response = await api.get('/plaid/status');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Flujo completo de conexión con Plaid
  async connectToPlaid() {
    try {
      // 1. Crear link token
      const linkTokenResponse = await this.createLinkToken();
      const linkToken = linkTokenResponse.link_token;
      console.log('Link token recibido:', linkToken);

      // 2. Abrir Plaid Link y obtener public token
      const publicToken = await this.openPlaidLink(linkToken);

      // 3. Intercambiar public token por access token
      const exchangeResponse = await this.exchangePublicToken(publicToken);

      return {
        success: true,
        message: 'Conectado exitosamente a Plaid',
        data: exchangeResponse
      };
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Abrir Plaid Link y obtener public token
  async openPlaidLink(linkToken) {
    return new Promise((resolve, reject) => {
      // Crear el script de Plaid Link si no existe
      if (!window.Plaid) {
        const script = document.createElement('script');
        script.src = 'https://cdn.plaid.com/link/v2/stable/link-initialize.js';
        script.onload = () => this.initializePlaidLink(linkToken, resolve, reject);
        script.onerror = () => reject(new Error('Failed to load Plaid Link'));
        document.head.appendChild(script);
      } else {
        this.initializePlaidLink(linkToken, resolve, reject);
      }
    });
  }

  // Inicializar Plaid Link
  initializePlaidLink(linkToken, resolve, reject) {
    const handler = window.Plaid.create({
      token: linkToken,
      onSuccess: (public_token, metadata) => {
        console.log('Plaid Link Success:', { public_token, metadata });
        resolve(public_token);
      },
      onExit: (err, metadata) => {
        console.log('Plaid Link Exit:', { err, metadata });
        if (err) {
          reject(new Error(err.error_message || 'User exited Plaid Link'));
        } else {
          reject(new Error('User cancelled Plaid Link'));
        }
      },
      onEvent: (eventName, metadata) => {
        console.log('Plaid Link Event:', eventName, metadata);
      }
    });

    handler.open();
  }

  // Manejo de errores
  handleError(error) {
    if (error.response) {
      return {
        message: error.response.data.message || 'Error del servidor',
        error: error.response.data.error || 'Error desconocido',
        status: error.response.status
      };
    } else if (error.request) {
      return {
        message: 'Error de conexión. Verifica tu conexión a internet.',
        error: 'Network Error',
        status: 0
      };
    } else {
      return {
        message: 'Error de configuración',
        error: error.message,
        status: 0
      };
    }
  }
}

const plaidService = new PlaidService();
export default plaidService; 