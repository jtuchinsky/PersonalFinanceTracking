import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import './App.css';

// Components
import AdminLogin from './components/AdminLogin';
import AdminDashboard from './components/AdminDashboard';

const BACKEND_URL = process.env.REACT_APP_ADMIN_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

// Auth Context
export const AuthContext = React.createContext();

function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('admin_token'));
  const [loading, setLoading] = useState(true);

  // Set axios default headers
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Check authentication on app load
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const userData = localStorage.getItem('admin_user');
          if (userData) {
            const parsedUser = JSON.parse(userData);
            if (parsedUser.is_admin) {
              setUser(parsedUser);
            } else {
              logout(); // Clear if not admin
            }
          }
        } catch (error) {
          console.error('Auth check failed:', error);
          logout();
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  const login = (userData, authToken) => {
    if (!userData.is_admin) {
      throw new Error('Admin access required');
    }

    setUser(userData);
    setToken(authToken);
    localStorage.setItem('admin_token', authToken);
    localStorage.setItem('admin_user', JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
  };

  const authContextValue = {
    user,
    token,
    login,
    logout,
    API
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={authContextValue}>
      <div className="App">
        <Router>
          <Routes>
            <Route
              path="/login"
              element={!user ? <AdminLogin /> : <Navigate to="/admin" />}
            />
            <Route
              path="/admin"
              element={user && user.is_admin ? <AdminDashboard /> : <Navigate to="/login" />}
            />
            <Route
              path="/"
              element={<Navigate to={user ? "/admin" : "/login"} />}
            />
          </Routes>
        </Router>
        <Toaster />
      </div>
    </AuthContext.Provider>
  );
}

export default App;