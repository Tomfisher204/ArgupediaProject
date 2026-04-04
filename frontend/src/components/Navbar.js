import React from 'react';
import {useNavigate, useLocation} from 'react-router-dom';
import {useAuth} from '../context';
import '../css/components/Navbar.css';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, user } = useAuth();
  const isActive = (path) => location.pathname === path;

  return (
    <header className="page-header">
      <div className="page-header-inner">
        <div className="header-logo" onClick={() => navigate('/dashboard')} style={{ cursor: 'pointer' }}>
          <span className="logo-mark-sm">A</span>
          <span className="logo-text-sm">argupedia</span>
        </div>
        <nav className="header-nav">
          <button className={`nav-link ${isActive('/themes') ? 'active' : ''}`} onClick={() => navigate('/themes')}>
            Themes
          </button>
          {user?.is_admin && (
            <button className={`nav-link ${isActive('/admin/schemes') ? 'active' : ''}`} onClick={() => navigate('/admin/schemes')}>
              Schemes
            </button>
          )}
        </nav>
        <button className="logout-btn" onClick={logout}>
          Log out
        </button>
      </div>
    </header>
  );
};

export default Navbar;