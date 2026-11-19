import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole } from '../types';
import { api } from '../api/client';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (u: string, p: string) => Promise<void>;
  register: (data: { username: string; email: string; full_name: string; role: string; password: string }) => Promise<void>;
  logout: () => void;
  switchRoleDemo: (role: UserRole) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      try {
        const u = await api.getMe();
        setUser(u);
      } catch (err) {
        console.warn('Initial session check:', err);
        // Fallback default demo user if not logged in
        setUser({
          id: 1,
          username: 'engineer',
          email: 'engineer@constructionsite.com',
          full_name: 'Marcus Vance, PE',
          role: 'site_engineer',
          is_active: true,
          created_at: new Date().toISOString()
        });
      } finally {
        setIsLoading(false);
      }
    }
    loadUser();
  }, [token]);

  const login = async (u: string, p: string) => {
    const data = await api.login(u, p);
    localStorage.setItem('token', data.access_token);
    setToken(data.access_token);
    setUser(data.user);
  };

  const register = async (data: { username: string; email: string; full_name: string; role: string; password: string }) => {
    const res = await api.register(data);
    localStorage.setItem('token', res.access_token);
    setToken(res.access_token);
    setUser(res.user);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser({
      id: 999,
      username: 'guest',
      email: 'guest@site.com',
      full_name: 'Guest Observer',
      role: 'inspector',
      is_active: true,
      created_at: new Date().toISOString()
    });
  };

  const switchRoleDemo = async (role: UserRole) => {
    try {
      if (role === 'admin') {
        await login('admin', 'Admin@123');
      } else if (role === 'site_engineer') {
        await login('engineer', 'Engineer@123');
      } else {
        await login('inspector', 'Inspector@123');
      }
    } catch {
      // In-memory fallback
      if (user) {
        setUser({
          ...user,
          role,
          full_name: role === 'admin' ? 'Sarah Jenkins (Admin)' : (role === 'site_engineer' ? 'Marcus Vance, PE' : 'Elena Rostova (Inspector)')
        });
      }
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout, switchRoleDemo }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
