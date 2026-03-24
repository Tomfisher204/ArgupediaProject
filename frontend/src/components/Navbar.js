import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';
 
const Navbar = () => {
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
 
  const navLinks = [
    { label: 'Home', to: '/' },
    { label: 'Dashboard', to: '/dashboard' },
    { label: 'Browse Arguments', to: '/arguments' },
  ];
 
  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-logo">
          <span className="logo-mark">A</span>
          <span className="logo-text">argupedia</span>
        </Link>
 
        <div className="navbar-links">
          {navLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={`nav-link ${location.pathname === link.to ? 'active' : ''}`}
            >
              {link.label}
            </Link>
          ))}
        </div>
 
        <div className="navbar-actions">
          <div className="user-pill">
            <div className="user-avatar">
              {/* Replace with real user initial */}
              U
            </div>
            <span className="user-name">[ username here ]</span>
          </div>
          <Link to="/new-argument" className="btn-new">
            + New Argument
          </Link>
        </div>
 
        <button className="mobile-menu-btn" onClick={() => setMenuOpen(!menuOpen)}>
          <span /><span /><span />
        </button>
      </div>
 
      {menuOpen && (
        <div className="mobile-menu">
          {navLinks.map((link) => (
            <Link key={link.to} to={link.to} className="mobile-nav-link" onClick={() => setMenuOpen(false)}>
              {link.label}
            </Link>
          ))}
          <Link to="/new-argument" className="mobile-nav-link cta">+ New Argument</Link>
        </div>
      )}
    </nav>
  );
};
 
export default Navbar;