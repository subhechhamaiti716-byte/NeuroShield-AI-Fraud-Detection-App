import React, { createContext, useState, useEffect } from 'react';
import { storage } from '../utils/storage';
import apiClient from '../api/axios';

type User = {
  id: number;
  name: string;
  email: string;
  balance: number;
};

type AuthContextType = {
  user: User | null;
  isLoading: boolean;
  login: (token: string, userData: User) => void;
  logout: () => void;
  fetchUser: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  login: () => {},
  logout: () => {},
  fetchUser: async () => {},
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUser = async () => {
    try {
      const token = await storage.getItem('token');
      if (token) {
        const response = await apiClient.get('/auth/me');
        setUser(response.data);
      }
    } catch (e) {
      console.error('Failed to fetch user', e);
      await storage.deleteItem('token');
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const login = async (token: string, userData: User) => {
    await storage.setItem('token', token);
    setUser(userData);
  };

  const logout = async () => {
    await storage.deleteItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, fetchUser }}>
      {children}
    </AuthContext.Provider>
  );
};
