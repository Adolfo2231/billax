import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Input from '../components/Input';
import Button from '../components/Button';
import './Login.css';

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

function ResetPassword() {
  const navigate = useNavigate();
  const query = useQuery();
  const token = query.get('token') || '';
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInputChange = (name, value) => {
    if (name === 'password') setPassword(value);
    if (name === 'confirmPassword') setConfirmPassword(value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    if (!token) {
      setError('Invalid or missing token.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(process.env.REACT_APP_API_BASE_URL + '/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: password })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || 'Error resetting password');
      setMessage('Password updated successfully! You can now sign in.');
      setTimeout(() => navigate('/login'), 2000);
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
        <div className="login-title">Reset your password</div>
        <div className="login-subtitle">Enter your new password</div>
        {error && <div className="login-error">{error}</div>}
        {message && <div className="login-error" style={{ background: '#f0fff4', color: '#388e3c', border: '1px solid #b2f2bb' }}>{message}</div>}
        <form className="login-form" onSubmit={handleSubmit} autoComplete="off">
          <Input
            label={null}
            name="password"
            type="password"
            value={password}
            onChange={handleInputChange}
            placeholder="New Password"
            required
            autoFocus
          />
          <Input
            label={null}
            name="confirmPassword"
            type="password"
            value={confirmPassword}
            onChange={handleInputChange}
            placeholder="Confirm New Password"
            required
          />
          <Button type="submit" className="login-btn" disabled={loading} loading={loading} style={{ width: '100%' }}>
            {loading ? 'Resetting...' : 'Reset Password'}
          </Button>
        </form>
      </div>
    </div>
  );
}

export default ResetPassword; 