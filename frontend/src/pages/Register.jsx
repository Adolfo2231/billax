import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Input from '../components/Input';
import Button from '../components/Button';
import './Login.css';
import authService from '../services/authService';

function Register() {
  const navigate = useNavigate();
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInputChange = (name, value) => {
    if (name === 'firstName') setFirstName(value);
    if (name === 'lastName') setLastName(value);
    if (name === 'email') setEmail(value);
    if (name === 'password') setPassword(value);
    if (name === 'confirmPassword') setConfirmPassword(value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    setLoading(true);
    try {
      await authService.register({
        first_name: firstName,
        last_name: lastName,
        email,
        password
      });
      setSuccess('Registration successful! Please sign in.');
      setTimeout(() => navigate('/login'), 2000);
    } catch (error) {
      setError(error.message);
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
        <div className="login-title">Create your account</div>
        <div className="login-subtitle">Sign up to use Billax</div>
        {error && <div className="login-error">{error}</div>}
        {success && <div className="login-error" style={{ background: '#f0fff4', color: '#388e3c', border: '1px solid #b2f2bb' }}>{success}</div>}
        <form className="login-form" onSubmit={handleSubmit} autoComplete="off">
          <Input
            label={null}
            name="firstName"
            type="text"
            value={firstName}
            onChange={handleInputChange}
            placeholder="First Name"
            required
            autoFocus
          />
          <Input
            label={null}
            name="lastName"
            type="text"
            value={lastName}
            onChange={handleInputChange}
            placeholder="Last Name"
            required
          />
          <Input
            label={null}
            name="email"
            type="email"
            value={email}
            onChange={handleInputChange}
            placeholder="Email Address"
            required
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
          <Input
            label={null}
            name="confirmPassword"
            type="password"
            value={confirmPassword}
            onChange={handleInputChange}
            placeholder="Confirm Password"
            required
          />
          <Button type="submit" className="login-btn" disabled={loading} loading={loading} style={{ width: '100%' }}>
            {loading ? 'Creating...' : 'Create Account'}
          </Button>
        </form>
        <div style={{ marginTop: '1.2rem', fontSize: '1rem' }}>
          Already have an account?{' '}
          <Link to="/login" className="login-link">Sign in here</Link>
        </div>
      </div>
    </div>
  );
}

export default Register; 