import React from 'react';
import {BrowserRouter as Router, Routes, Route, Navigate} from 'react-router-dom';
import {AuthProvider, useAuth} from './context/AuthContext';
import {LandingPage, Dashboard, AdminDashboard, ThemesPage, ThemeArgumentsPage, ArgumentPage} from './pages';
import './css/App.css';

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

const AppRoutes = () => {
  const { user } = useAuth();
  const isAdmin = user?.is_admin;

  return (
    <Routes>
      <Route path="/" element={<PublicRoute><LandingPage /></PublicRoute>} />
      <Route path="/dashboard" element={<PrivateRoute>{isAdmin ? <Navigate to="/admin-dashboard" replace /> : <Dashboard />}</PrivateRoute>} />
      <Route path="/admin-dashboard" element={<PrivateRoute>{isAdmin ? <AdminDashboard /> : <Navigate to="/dashboard" replace />}</PrivateRoute>} />
      <Route path="/themes" element={<PrivateRoute><ThemesPage /></PrivateRoute>} />
      <Route path="/themes/:themeId" element={<PrivateRoute><ThemeArgumentsPage /></PrivateRoute>} />
      <Route path="/arguments/*" element={<PrivateRoute><ArgumentPage /></PrivateRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

const App = () => (
  <AuthProvider>
    <Router>
      <AppRoutes />
    </Router>
  </AuthProvider>
);

export default App;