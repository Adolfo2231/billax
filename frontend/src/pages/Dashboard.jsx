import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import accountsService from '../services/accountsService';
import transactionService from '../services/transactionService';
import './Dashboard.css';
import { formatCurrency, formatDate, getAccountIcon } from '../utils/format';

function Dashboard() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState({
    totalBalance: 0,
    totalAccounts: 0,
    recentTransactions: 0,
    monthlySpending: 0
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch accounts and transactions in parallel
      const [accountsData, transactionsData] = await Promise.all([
        accountsService.getAccounts().catch(() => ({ accounts: [] })),
        transactionService.getTransactions(10, 0).catch(() => ({ transactions: [] }))
      ]);

      const accountsList = accountsData.accounts || accountsData || [];
      const transactionsList = transactionsData.transactions || transactionsData || [];

      setAccounts(accountsList);
      setTransactions(transactionsList);

      // Calculate summary
      const totalBalance = accountsList.reduce((sum, account) => sum + (account.balances?.current || 0), 0);
      const monthlySpending = transactionsList
        .filter(t => new Date(t.date) >= new Date(new Date().getFullYear(), new Date().getMonth(), 1))
        .reduce((sum, t) => sum + Math.abs(t.amount || 0), 0);

      setSummary({
        totalBalance,
        totalAccounts: accountsList.length,
        recentTransactions: transactionsList.length,
        monthlySpending
      });

    } catch (err) {
      setError('Error loading dashboard data. Please try again.');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Eliminar funciones formatCurrency, formatDate y getTransactionIcon locales

  if (loading) {
    return (
      <Layout>
        <div className="dashboard-container">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading your financial dashboard...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="dashboard-container">
        <div className="dashboard-content">
          {/* Header */}
          <div className="dashboard-header">
            <div className="header-content">
              <div>
                <h1>Welcome back, {user?.name || user?.first_name || 'User'}! 👋</h1>
                <p>Here's your financial overview for today</p>
              </div>
              <div className="header-actions">
                <button 
                  className="btn-sync"
                  onClick={fetchDashboardData}
                  disabled={loading}
                >
                  🔄 Refresh
                </button>
              </div>
            </div>
          </div>

          {error && (
            <div className="error-message">
              <p>{error}</p>
              <button onClick={fetchDashboardData}>Try Again</button>
            </div>
          )}

          {/* Financial Summary Cards */}
          <div className="summary-cards">
            <div className="summary-card primary">
              <div className="card-content">
                <div className="card-icon">💰</div>
                <div className="card-info">
                  <h3>Total Balance</h3>
                  <p className="amount">{formatCurrency(summary.totalBalance)}</p>
                  <span className="subtitle">{summary.totalAccounts} accounts</span>
                </div>
              </div>
            </div>

            <div className="summary-card">
              <div className="card-content">
                <div className="card-icon">🏦</div>
                <div className="card-info">
                  <h3>Connected Accounts</h3>
                  <p className="amount">{summary.totalAccounts}</p>
                  <span className="subtitle">Bank accounts</span>
                </div>
              </div>
            </div>

            <div className="summary-card">
              <div className="card-content">
                <div className="card-icon">📊</div>
                <div className="card-info">
                  <h3>Monthly Spending</h3>
                  <p className="amount">{formatCurrency(summary.monthlySpending)}</p>
                  <span className="subtitle">This month</span>
                </div>
              </div>
            </div>

            <div className="summary-card">
              <div className="card-content">
                <div className="card-icon">📈</div>
                <div className="card-info">
                  <h3>Recent Activity</h3>
                  <p className="amount">{summary.recentTransactions}</p>
                  <span className="subtitle">Last 10 transactions</span>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content Grid */}
          <div className="dashboard-grid">
            {/* Quick Actions */}
            <div className="dashboard-section">
              <h2>Quick Actions</h2>
              <div className="action-cards">
                <div className="action-card" onClick={() => navigate('/accounts')}>
                  <div className="action-icon">🏦</div>
                  <h3>Manage Accounts</h3>
                  <p>View and sync your bank accounts</p>
                </div>
                
                <div className="action-card" onClick={() => navigate('/transactions')}>
                  <div className="action-icon">💳</div>
                  <h3>View Transactions</h3>
                  <p>See all your transaction history</p>
                </div>
                
                <div className="action-card" onClick={() => navigate('/chat')}>
                  <div className="action-icon">🤖</div>
                  <h3>AI Assistant</h3>
                  <p>Get financial insights and advice</p>
                </div>
                
                <div className="action-card disabled">
                  <div className="action-icon">📊</div>
                  <h3>Analytics</h3>
                  <p>Coming soon - Detailed reports</p>
                </div>
              </div>
            </div>

            {/* Recent Transactions */}
            <div className="dashboard-section">
              <div className="section-header">
                <h2>Recent Transactions</h2>
                <button 
                  className="btn-view-all"
                  onClick={() => navigate('/transactions')}
                >
                  View All
                </button>
              </div>
              
              {transactions.length > 0 ? (
                <div className="transactions-list">
                  {transactions.slice(0, 5).map((transaction) => (
                    <div key={transaction.id || transaction._id || transaction.date+transaction.amount} className="transaction-item">
                      <div className="transaction-icon">
                        {getAccountIcon(transaction.category?.[0])}
                      </div>
                      <div className="transaction-details">
                        <h4>{transaction.name || 'Unknown Transaction'}</h4>
                        <p>{transaction.merchant_name || transaction.category?.[0] || 'Other'}</p>
                        <span className="transaction-date">{formatDate(transaction.date)}</span>
                      </div>
                      <div className="transaction-amount">
                        <span className={transaction.amount < 0 ? 'negative' : 'positive'}>
                          {formatCurrency(Math.abs(transaction.amount))}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">📝</div>
                  <p>No transactions found</p>
                  <button 
                    className="btn-primary"
                    onClick={() => navigate('/transactions')}
                  >
                    Sync Transactions
                  </button>
                </div>
              )}
            </div>

            {/* Account Balances */}
            <div className="dashboard-section">
              <div className="section-header">
                <h2>Account Balances</h2>
                <button 
                  className="btn-view-all"
                  onClick={() => navigate('/accounts')}
                >
                  Manage
                </button>
              </div>
              
              {accounts.length > 0 ? (
                <div className="accounts-list">
                  {accounts.slice(0, 3).map((account) => (
                    <div key={account.account_id || account.id || account.name} className="account-item">
                      <div className="account-info">
                        <h4>{account.name}</h4>
                        <p>{account.type} • {account.subtype}</p>
                        <span className="account-number">****{account.mask}</span>
                      </div>
                      <div className="account-balance">
                        <span className="balance-amount">
                          {formatCurrency(account.balances?.current)}
                        </span>
                        <span className="balance-label">Available</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">🏦</div>
                  <p>No accounts connected</p>
                  <button 
                    className="btn-primary"
                    onClick={() => navigate('/accounts')}
                  >
                    Connect Account
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default Dashboard; 