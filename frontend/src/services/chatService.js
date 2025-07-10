import api from './api';

const chatService = {
  // Obtener historial de chat
  async getChatHistory() {
    try {
      const response = await api.get('/chat/history');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error fetching chat history');
    }
  },

  // Enviar mensaje al chat/IA
  async sendMessage(message, selectedAccountId = null) {
    try {
      const payload = { message };
      if (selectedAccountId) {
        payload.selected_account_id = selectedAccountId;
      }
      const response = await api.post('/chat/', payload);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error sending message');
    }
  },

  // Eliminar un mensaje de chat
  async deleteChat(chatId) {
    try {
      const response = await api.delete(`/chat/delete/${chatId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error deleting chat message');
    }
  },

  // Eliminar todo el historial de chat
  async deleteAllChats() {
    try {
      const response = await api.delete('/chat/delete/all');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Error deleting all chat messages');
    }
  }
};

export default chatService; 