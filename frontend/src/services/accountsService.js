import api from './api';

class AccountsService {
  // Obtener todas las cuentas del usuario
  async getAccounts() {
    try {
      const response = await api.get('/accounts/');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Sincronizar cuentas con Plaid
  async syncAccounts() {
    try {
      const response = await api.post('/accounts/sync-accounts');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Obtener una cuenta específica por ID
  async getAccountById(accountId) {
    try {
      const response = await api.get(`/accounts/${accountId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Obtener cuentas por tipo
  async getAccountsByType(accountType) {
    try {
      const response = await api.get(`/accounts/${accountType}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Eliminar todas las cuentas del usuario
  async deleteAllAccounts() {
    try {
      const response = await api.delete('/accounts');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Eliminar una cuenta específica
  async deleteAccount(accountId) {
    try {
      const response = await api.delete(`/accounts/delete/${accountId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Obtener resumen de cuentas
  async getAccountsSummary() {
    try {
      const response = await api.get('/accounts/summary');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
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

const accountsService = new AccountsService();
export default accountsService; 