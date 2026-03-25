import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LandingPage          from './pages/LandingPage';
import Dashboard            from './pages/Dashboard';
import ThemesPage           from './pages/ThemesPage';
import ThemeArgumentsPage   from './pages/ThemeArgumentsPage';
import ArgumentPage         from './pages/ArgumentPage';
import './App.css';

const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return null;
  return user ? <Navigate to="/dashboard" replace /> : children;
};

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return null;
  return user ? children : <Navigate to="/" replace />;
};

const AppRoutes = () => (
  <Routes>
    <Route path="/" element={<PublicRoute><LandingPage /></PublicRoute>} />
    <Route path="/dashboard"             element={<PrivateRoute><Dashboard /></PrivateRoute>} />
    <Route path="/themes"                element={<PrivateRoute><ThemesPage /></PrivateRoute>} />
    <Route path="/themes/:themeId"       element={<PrivateRoute><ThemeArgumentsPage /></PrivateRoute>} />
    <Route path="/arguments/*" element={<PrivateRoute><ArgumentPage /></PrivateRoute>} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);

const App = () => (
  <AuthProvider>
    <Router>
      <AppRoutes />
    </Router>
  </AuthProvider>
);

export default App;