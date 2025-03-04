import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';
import axios from 'axios';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  // Initialize auth state from localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
        // Set axios default authorization header
        axios.defaults.headers.common['Authorization'] = `Bearer ${parsedUser.token}`;
      } catch (error) {
        console.error('Error parsing stored user:', error);
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      // In a real application, make an API call to your backend
      // For now, we'll simulate a successful login
      const mockUser = {
        id: '1',
        username,
        token: 'mock-jwt-token',
        role: 'admin'
      };

      // Store user in localStorage
      localStorage.setItem('user', JSON.stringify(mockUser));
      
      // Set user in state
      setUser(mockUser);
      
      // Set axios default authorization header
      axios.defaults.headers.common['Authorization'] = `Bearer ${mockUser.token}`;
      
      enqueueSnackbar('Successfully logged in', { variant: 'success' });
      navigate('/dashboard');
      
      return true;
    } catch (error) {
      console.error('Login error:', error);
      enqueueSnackbar(error.message || 'Login failed', { variant: 'error' });
      return false;
    }
  };

  const logout = () => {
    try {
      // Clear user from localStorage
      localStorage.removeItem('user');
      
      // Clear user from state
      setUser(null);
      
      // Remove axios default authorization header
      delete axios.defaults.headers.common['Authorization'];
      
      enqueueSnackbar('Successfully logged out', { variant: 'success' });
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
      enqueueSnackbar('Error during logout', { variant: 'error' });
    }
  };

  const updateUser = (updates) => {
    try {
      const updatedUser = { ...user, ...updates };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      setUser(updatedUser);
    } catch (error) {
      console.error('Error updating user:', error);
      enqueueSnackbar('Error updating user information', { variant: 'error' });
    }
  };

  // Handle 401 Unauthorized responses
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          logout();
        }
        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, []);

  const value = {
    user,
    loading,
    login,
    logout,
    updateUser,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
