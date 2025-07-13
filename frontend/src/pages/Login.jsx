import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Input from '../components/Input';
import Button from '../components/Button';
import './Login.css';
import { useAuth } from '../contexts/AuthContext';

function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInputChange = (name, value) => {
    if (name === 'email') setEmail(value);
    if (name === 'password') setPassword(value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login({ email, password });
      navigate('/dashboard');
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
        <div className="login-title">Welcome Back</div>
        <div className="login-subtitle">Sign in to your Billax account</div>
        {error && <div className="login-error">{error}</div>}
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
          <Input
            label={null}
            name="password"
            type="password"
            value={password}
            onChange={handleInputChange}
            placeholder="Password"
            required
          />
          <Button type="submit" className="login-btn" disabled={loading} loading={loading} style={{ width: '100%' }}>
            {loading ? 'Signing in...' : '➜ Sign In'}
          </Button>
        </form>
        <div style={{ marginTop: '0.8rem', fontSize: '1rem' }}>
          <Link to="/forgot-password" className="login-link">Forgot your password?</Link>
        </div>
        <div style={{ marginTop: '1.2rem', fontSize: '1rem' }}>
          Don't have an account?{' '}
          <Link to="/register" className="login-link">Register here</Link>
        </div>
      </div>
    </div>
  );
}

export default Login; 