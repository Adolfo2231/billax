import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const isActive = (path) => {
    return location.pathname === path;
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/accounts', label: 'Accounts', icon: '🏦' },
    { path: '/transactions', label: 'Transactions', icon: '💳' },
    { path: '/chat', label: 'Chat', icon: '💬' },
    // Puedes agregar más enlaces aquí
    // { path: '/analytics', label: 'Analytics', icon: '📈' },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo */}
        <div className="navbar-logo" onClick={() => navigate('/dashboard')}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 17V7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M3 17l4-4a2 2 0 0 1 2.83 0l2.34 2.34a2 2 0 0 0 2.83 0L21 9" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span>Billax</span>
        </div>

        {/* Desktop Navigation */}
        <div className="navbar-nav">
          {navItems.map((item) => (
            <button
              key={item.path}
              className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
              onClick={() => navigate(item.path)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
        </div>

        {/* User Menu */}
        <div className="navbar-user">
          <div className="user-info">
            <span className="user-name">
              {user?.name || user?.first_name || 'User'}
            </span>
            <span className="user-email">{user?.email}</span>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            <span className="logout-label">Logout</span>
          </button>
        </div>

        {/* Mobile Menu Button */}
        <button 
          className="mobile-menu-btn"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          <span className={`hamburger ${isMenuOpen ? 'open' : ''}`}></span>
        </button>
      </div>

      {/* Mobile Menu */}
      <div className={`mobile-menu ${isMenuOpen ? 'open' : ''}`}>
        {navItems.map((item) => (
          <button
            key={item.path}
            className={`mobile-nav-item ${isActive(item.path) ? 'active' : ''}`}
            onClick={() => {
              navigate(item.path);
              setIsMenuOpen(false);
            }}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
        <div className="mobile-user-info">
          <span className="user-name">
            {user?.name || user?.first_name || 'User'}
          </span>
          <span className="user-email">{user?.email}</span>
        </div>
        <button 
          className="mobile-logout-btn" 
          onClick={() => {
            handleLogout();
            setIsMenuOpen(false);
          }}
        >
          <span className="logout-label">Logout</span>
        </button>
      </div>
    </nav>
  );
};

export default Navbar; 