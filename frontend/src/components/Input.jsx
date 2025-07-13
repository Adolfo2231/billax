import React, { useState } from 'react';

function getIcon(type) {
  if (type === 'email') {
    return (
      <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z"/><path d="M2 20c0-4 4-7 10-7s10 3 10 7"/></svg>
    );
  }
  if (type === 'password') {
    return (
      <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
    );
  }
  // Default: user icon
  return (
    <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z"/><path d="M2 20c0-4 4-7 10-7s10 3 10 7"/></svg>
  );
}

const Input = ({
  label,
  name,
  type = 'text',
  value,
  onChange,
  error,
  placeholder,
  required = false,
  disabled = false,
  autoFocus = false,
}) => {
  const [show, setShow] = useState(false);
  const isPassword = type === 'password';
  const inputType = isPassword && show ? 'text' : type;

  return (
    <div className="input-group" style={{ marginBottom: '1.2rem' }}>
      {label && (
        <label htmlFor={name} style={{ display: 'block', marginBottom: 4, fontWeight: 500 }}>{label}{required && <span style={{ color: '#d32f2f', marginLeft: 2 }}>*</span>}</label>
      )}
      <span className="input-icon">{getIcon(type)}</span>
      <input
        id={name}
        name={name}
        type={inputType}
        value={value}
        onChange={e => onChange(name, e.target.value)}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        autoFocus={autoFocus}
        className="w-full px-3 py-2 border rounded-md"
        style={{ paddingLeft: 36, paddingRight: isPassword ? 36 : 12, color: '#222', background: '#fff' }}
      />
      {isPassword && (
        <button
          type="button"
          className="input-toggle"
          tabIndex={-1}
          onClick={() => setShow(v => !v)}
          aria-label={show ? 'Hide password' : 'Show password'}
        >
          {show ? (
            <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M17.94 17.94A10.06 10.06 0 0 1 12 20c-5 0-9.27-3.11-10-7.5a9.77 9.77 0 0 1 3.07-5.16M6.53 6.53A9.77 9.77 0 0 1 12 4c5 0 9.27 3.11 10 7.5a9.93 9.93 0 0 1-4.29 5.61"/><path d="M1 1l22 22"/></svg>
          ) : (
            <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><ellipse cx="12" cy="12" rx="10" ry="7.5"/><circle cx="12" cy="12" r="3"/></svg>
          )}
        </button>
      )}
      {error && (
        <p style={{ color: '#d32f2f', marginTop: 4, fontSize: 14 }}>{error}</p>
      )}
    </div>
  );
};

export default Input; 