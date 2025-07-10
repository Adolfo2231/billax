import React from 'react';
import { useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import FloatingChat from './FloatingChat';
import './Layout.css';

const Layout = ({ children }) => {
  const location = useLocation();
  const isChatPage = location.pathname === '/chat';

  return (
    <div className="layout">
      <Navbar />
      <main className="layout-main">
        {children}
      </main>
      {!isChatPage && <FloatingChat />}
    </div>
  );
};

export default Layout; 