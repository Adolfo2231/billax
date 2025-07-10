import api from './api';

class AuthService {
  // Registro de usuario
  async register(userData) {
    try {
      const response = await api.post('/auth/register', userData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Login de usuario
  async login(credentials) {
    try {
      const response = await api.post('/auth/login', credentials);
      // Guardar token y datos del usuario en localStorage
      if (response.data.token) {
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Solicitar reset de contraseña
  async forgotPassword(email) {
    try {
      const response = await api.post('/auth/forgot-password', { email });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Reset de contraseña con token
  async resetPassword(token, newPassword) {
    try {
      const response = await api.post('/auth/reset-password', {
        token,
        new_password: newPassword
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Logout
  async logout() {
    try {
      const response = await api.post('/auth/logout');
      // Limpiar localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      return response.data;
    } catch (error) {
      // Aunque falle la petición, limpiar localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      throw this.handleError(error);
    }
  }

  // Verificar si el usuario está autenticado
  isAuthenticated() {
    return !!localStorage.getItem('token');
  }

  // Obtener datos del usuario actual
  getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  // Obtener token actual
  getToken() {
    return localStorage.getItem('token');
  }

  // Manejo de errores
  handleError(error) {
    if (error.response) {
      // Error de respuesta del servidor
      return {
        message: error.response.data.message || 'Error del servidor',
        error: error.response.data.error || 'Error desconocido',
        status: error.response.status
      };
    } else if (error.request) {
      // Error de red
      return {
        message: 'Error de conexión. Verifica tu conexión a internet.',
        error: 'Network Error',
        status: 0
      };
    } else {
      // Error de configuración
      return {
        message: 'Error de configuración',
        error: error.message,
        status: 0
      };
    }
  }
}

const authService = new AuthService();
export default authService; 