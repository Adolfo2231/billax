import api from './api';

const transactionService = {
  // Obtener todas las transacciones del usuario
  async getTransactions(limit = null, offset = 0, startDate = null, endDate = null) {
    try {
      const params = { offset };
      if (limit) params.limit = limit;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      const response = await api.get('/transaction/transactions', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error fetching transactions');
    }
  },

  // Sincronizar transacciones desde Plaid
  async syncTransactions(startDate = null, endDate = null, count = null) {
    try {
      const params = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      if (count) params.count = count;
      
      const response = await api.post('/transaction/sync-transactions', null, { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error syncing transactions');
    }
  },

  // Obtener una transacción específica por ID
  async getTransactionById(transactionId) {
    try {
      const response = await api.get(`/transaction/${transactionId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error fetching transaction');
    }
  },

  // Obtener transacciones por tipo
  async getTransactionsByType(transactionType) {
    try {
      const response = await api.get(`/transaction/by-type/${transactionType}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error fetching transactions by type');
    }
  },

  // Obtener resumen de transacciones
  async getTransactionSummary() {
    try {
      const response = await api.get('/transaction/summary');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error fetching transaction summary');
    }
  },

  // Eliminar una transacción específica
  async deleteTransaction(transactionId) {
    try {
      const response = await api.delete(`/transaction/${transactionId}/delete`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error deleting transaction');
    }
  },

  // Eliminar todas las transacciones del usuario
  async deleteAllTransactions() {
    try {
      const response = await api.delete('/transaction/delete-all');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error deleting all transactions');
    }
  }
};

export default transactionService; 