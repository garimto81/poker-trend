import { useState, useEffect } from 'react';
import { mockApi } from '../services/mockApi';
import { USE_MOCK_DATA } from '../config/api';

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  avatar?: string;
}

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = () => {
    const token = localStorage.getItem('auth_token');
    
    if (token) {
      if (USE_MOCK_DATA) {
        // Mock 데이터 사용 시
        setUser({
          id: 1,
          username: 'admin',
          email: 'admin@poker-trend.com',
          role: 'admin',
          avatar: '/api/placeholder/50/50',
        });
        setIsAuthenticated(true);
      } else {
        // 실제 API 호출 시 여기에 구현
        setIsAuthenticated(true);
      }
    } else if (USE_MOCK_DATA) {
      // GitHub Pages에서는 자동 로그인 (데모용)
      login('admin', 'admin');
      return;
    }
    
    setIsLoading(false);
  };

  const login = async (username: string, password: string) => {
    try {
      setIsLoading(true);
      
      if (USE_MOCK_DATA) {
        const result = await mockApi.login({ username, password });
        setUser(result.user);
        setIsAuthenticated(true);
      } else {
        // 실제 API 호출
        // const result = await api.login({ username, password });
        // setUser(result.user);
        // setIsAuthenticated(true);
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      if (USE_MOCK_DATA) {
        await mockApi.logout();
      } else {
        // 실제 API 호출
        // await api.logout();
      }
      
      setUser(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return {
    isAuthenticated,
    user,
    isLoading,
    login,
    logout,
  };
};