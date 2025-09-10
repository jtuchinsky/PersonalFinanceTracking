import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import './App.css';

// Components
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import TransactionForm from './components/TransactionForm';
import TransactionList from './components/TransactionList';
import AddAccount from './components/AddAccount';
import AccountManager from './components/AccountManager';
import EditAccount from './components/EditAccount';
import SankeyDiagram from './components/SankeyDiagram';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
export const AuthContext = React.createContext();

function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
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
          // You could add a /me endpoint to verify token, for now just trust local storage
          const userData = localStorage.getItem('user');
          if (userData) {
            setUser(JSON.parse(userData));
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
    setUser(userData);
    setToken(authToken);
    localStorage.setItem('token', authToken);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
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
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
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
              element={!user ? <Login /> : <Navigate to="/dashboard" />} 
            />
            <Route 
              path="/register" 
              element={!user ? <Register /> : <Navigate to="/dashboard" />} 
            />
            <Route 
              path="/dashboard" 
              element={user ? <Dashboard /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/transactions" 
              element={user ? <TransactionList /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/add-transaction" 
              element={user ? <TransactionForm /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/add-account" 
              element={user ? <AddAccount /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/manage-accounts" 
              element={user ? <AccountManager /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/edit-account/:accountId" 
              element={user ? <EditAccount /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/analytics" 
              element={user ? <SankeyDiagram /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/" 
              element={<Navigate to={user ? "/dashboard" : "/login"} />} 
            />
          </Routes>
        </Router>
        <Toaster />
      </div>
    </AuthContext.Provider>
  );
}

export default App;