import React, { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(!!authService.getToken());
  const [user, setUser] = useState(authService.getCurrentUser());
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsAuthenticated(!!authService.getToken());
    setUser(authService.getCurrentUser());
  }, []);

  const login = async (credentials) => {
    setIsLoading(true);
    try {
      await authService.login(credentials);
      setIsAuthenticated(true);
      setUser(authService.getCurrentUser());
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await authService.logout();
    } finally {
      setIsAuthenticated(false);
      setUser(null);
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext); 