import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Input from '../components/Input';
import Button from '../components/Button';
import './Login.css';
import authService from '../services/authService';

function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => {
        navigate('/login');
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [message, navigate]);

  const handleInputChange = (name, value) => {
    setEmail(value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);
    try {
      await authService.forgotPassword(email);
      setMessage('If the email exists, you will receive a reset link.');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-bg">
      <div className="login-card">
        <div className="login-logo">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 17V7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M3 17l4-4a2 2 0 0 1 2.83 0l2.34 2.34a2 2 0 0 0 2.83 0L21 9" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
          <span>Billax</span>
        </div>
        <div className="login-title">Forgot your password?</div>
        <div className="login-subtitle">Enter your email to receive a reset link</div>
        {error && <div className="login-error">{error}</div>}
        {message && <div className="login-error" style={{ background: '#f0fff4', color: '#388e3c', border: '1px solid #b2f2bb' }}>{message}<br />Redirecting to login...</div>}
        <form className="login-form" onSubmit={handleSubmit} autoComplete="off">
          <Input
            label={null}
            name="email"
            type="email"
            value={email}
            onChange={handleInputChange}
            placeholder="Email Address"
            required
            autoFocus
          />
          <Button type="submit" className="login-btn" disabled={loading} loading={loading} style={{ width: '100%' }}>
            {loading ? 'Sending...' : 'Send Reset Link'}
          </Button>
        </form>
      </div>
    </div>
  );
}

export default ForgotPassword; 