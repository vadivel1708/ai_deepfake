import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('token') || null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifyUser = async () => {
      if (token) {
        try {
          const res = await authAPI.getMe();
          setUser(res.data);
          localStorage.setItem('user', JSON.stringify(res.data));
        } catch {
          logout();
        }
      }
      setLoading(false);
    };
    verifyUser();
  }, [token]);

  const login = async (email, password) => {
    const res = await authAPI.login(email, password);
    const data = res.data;
    localStorage.setItem('token', data.access_token);
    const userData = {
      id: data.user_id,
      email: data.email,
      full_name: data.full_name,
      role: data.role,
    };
    localStorage.setItem('user', JSON.stringify(userData));
    setToken(data.access_token);
    setUser(userData);
    return userData;
  };

  const register = async (email, password, fullName, role = 'user') => {
    await authAPI.register(email, password, fullName, role);
    return await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthenticated: !!user,
        isReviewer: user?.role === 'reviewer' || user?.role === 'admin',
        isAdmin: user?.role === 'admin',
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
