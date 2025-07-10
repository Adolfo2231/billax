import React, { useState, useEffect } from 'react';
import Button from '../components/Button';
import Layout from '../components/Layout';
import accountsService from '../services/accountsService';
import plaidService from '../services/plaidService';
import './Accounts.css';
import { formatCurrency, getAccountIcon } from '../utils/format';

function Accounts() {
  // const navigate = useNavigate(); // Removed unused variable
  const [accounts, setAccounts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [plaidStatus, setPlaidStatus] = useState(false);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadAccountsData();
  }, []);

  // Solo carga cuentas y resumen, no sincroniza con Plaid automáticamente
  const loadAccountsData = async () => {
    try {
      setLoading(true);
      setError('');
      // Verificar estado de Plaid
      const statusResponse = await plaidService.getStatus();
      setPlaidStatus(statusResponse.linked);
      if (statusResponse.linked) {
        // Solo obtener cuentas y resumen, no sincronizar
        const accountsResponse = await accountsService.getAccounts();
        setAccounts(accountsResponse.accounts || []);
        const summaryResponse = await accountsService.getAccountsSummary();
        setSummary(summaryResponse.summary || null);
      }
    } catch (err) {
      setError(err.message || 'Error loading accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleConnectPlaid = async () => {
    try {
      setConnecting(true);
      setError('');
      setSuccess('');
      setSuccess('Iniciando conexión con Plaid...');
      const result = await plaidService.connectToPlaid();
      setSuccess(result.message);
      setPlaidStatus(true);
      // Sincronizar cuentas inmediatamente después de conectar
      await loadAccountsData();
    } catch (err) {
      if (err.message.includes('cancelled') || err.message.includes('exited')) {
        setError('Conexión cancelada por el usuario');
      } else {
        setError(err.message || 'Error connecting to Plaid');
      }
    } finally {
      setConnecting(false);
    }
  };

  // Sincroniza solo cuando el usuario lo pide
  const handleSyncAccounts = async () => {
    try {
      setLoading(true);
      setError('');
      setSuccess('');
      const response = await accountsService.syncAccounts();
      setAccounts(response.accounts || []);
      setSuccess('Accounts synchronized successfully');
      // Recargar resumen
      const summaryResponse = await accountsService.getAccountsSummary();
      setSummary(summaryResponse.summary || null);
    } catch (err) {
      setError(err.message || 'Error syncing accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnectPlaid = async () => {
    try {
      setLoading(true);
      setError('');
      
      await plaidService.disconnect();
      setPlaidStatus(false);
      setAccounts([]);
      setSummary(null);
      setSuccess('Disconnected from Plaid successfully');
      
    } catch (err) {
      setError(err.message || 'Error disconnecting from Plaid');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !plaidStatus) {
    return (
      <Layout>
        <div className="accounts-container">
          <div className="loading-spinner">Loading...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="accounts-container">
        <div className="transactions-card">
          <div className="transactions-header">
            <div className="transactions-logo">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 17V7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M3 17l4-4a2 2 0 0 1 2.83 0l2.34 2.34a2 2 0 0 0 2.83 0L21 9" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span>Billax</span>
            </div>
            <div className="transactions-title">Your Accounts</div>
            <div className="transactions-subtitle">Manage your financial accounts</div>
          </div>

          {error && <div className="transactions-error">{error}</div>}
          {success && <div className="transactions-success">{success}</div>}

          {!plaidStatus ? (
            <div className="plaid-connect-section">
              <div className="plaid-icon">🏦</div>
              <h3>Connect Your Bank</h3>
              <p>Link your bank accounts to start managing your finances with Billax</p>
              <div className="plaid-steps">
                <div className="step">
                  <span className="step-number">1</span>
                  <span className="step-text">Create secure connection</span>
                </div>
                <div className="step">
                  <span className="step-number">2</span>
                  <span className="step-text">Select your bank</span>
                </div>
                <div className="step">
                  <span className="step-number">3</span>
                  <span className="step-text">Access your accounts</span>
                </div>
              </div>
              <Button 
                onClick={handleConnectPlaid}
                disabled={connecting}
                loading={connecting}
                className="sync-btn"
              >
                {connecting ? 'Connecting...' : '🔗 Connect with Plaid'}
              </Button>
              <div className="plaid-note">
                <p>🔒 Your data is encrypted and secure. We never store your bank credentials.</p>
              </div>
            </div>
          ) : (
            <div className="transactions-content">
              <div className="transactions-actions">
                <Button 
                  onClick={handleSyncAccounts}
                  disabled={loading}
                  className="sync-btn"
                >
                  🔄 Sync Accounts
                </Button>
                <Button 
                  onClick={handleDisconnectPlaid}
                  disabled={loading}
                  className="delete-all-btn"
                >
                  ❌ Disconnect
                </Button>
              </div>

              {summary && (
                <div className="transactions-summary">
                  <div className="summary-card">
                    <div className="summary-icon">💰</div>
                    <div className="summary-info">
                      <div className="summary-label">Total Balance</div>
                      <div className="summary-value positive">{formatCurrency(summary.total_balance)}</div>
                      <div className="summary-label" style={{ fontSize: 13 }}>{summary.total_accounts} accounts</div>
                    </div>
                  </div>
                </div>
              )}

              <div className="transactions-account-group">
                <div className="account-group-header" style={{ marginBottom: 8 }}>
                  <span className="account-group-icon">🏦</span>
                  <span className="account-group-name">Your Accounts ({accounts.length})</span>
                </div>
                {accounts.length === 0 ? (
                  <div style={{ textAlign: 'center', color: '#888', margin: '2rem 0' }}>
                    No accounts found. Try syncing your accounts.
                  </div>
                ) : (
                  <div className="accounts-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 20 }}>
                    {accounts.map((account) => (
                      <div key={account.account_id} className="account-card transaction-card" style={{ borderRadius: 16, boxShadow: '0 2px 8px rgba(31,38,135,0.08)', padding: 20, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: 160 }}>
                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 10 }}>
                          <span className="account-icon transaction-icon" style={{ fontSize: 28, marginRight: 12 }}>{getAccountIcon(account.type)}</span>
                          <div style={{ flex: 1 }}>
                            <div className="account-name transaction-description" style={{ fontWeight: 600, fontSize: 17 }}>{account.name}</div>
                            <div className="account-type transaction-account-name" style={{ color: '#888', fontSize: 13 }}>{account.type} • {account.subtype}</div>
                          </div>
                          <button
                            className="delete-transaction-btn"
                            title="Delete account"
                            onClick={async () => {
                              if (window.confirm('Are you sure you want to delete this account? This action cannot be undone.')) {
                                try {
                                  setLoading(true);
                                  setError('');
                                  await accountsService.deleteAccount(account.id);
                                  setSuccess('Account deleted successfully');
                                  // Recargar cuentas
                                  loadAccountsData();
                                } catch (err) {
                                  setError(err.message || 'Error deleting account');
                                } finally {
                                  setLoading(false);
                                }
                              }
                            }}
                            style={{ marginLeft: 8 }}
                          >
                            🗑️
                          </button>
                        </div>
                        <div style={{ marginTop: 8 }}>
                          <div className="balance-amount transaction-amount" style={{ fontSize: 22, fontWeight: 700 }}>
                            {formatCurrency(account.balances?.current || 0)}
                          </div>
                          <div className="balance-label transaction-account-name" style={{ color: '#888', fontSize: 13 }}>Current Balance</div>
                          {account.balances?.available && (
                            <div className="transaction-type" style={{ color: '#388e3c', fontWeight: 500, fontSize: 15, marginTop: 2 }}>
                              Available: {formatCurrency(account.balances.available)}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

export default Accounts; 