import React, { useState, useEffect, useCallback } from 'react';
import Button from '../components/Button';
import Layout from '../components/Layout';
import transactionService from '../services/transactionService';
import accountsService from '../services/accountsService';
import './Transactions.css';
import { formatCurrency, formatDate, getAccountIcon } from '../utils/format';

function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [allTransactions, setAllTransactions] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [accountsMap, setAccountsMap] = useState({});
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterAccount, setFilterAccount] = useState('all');
  const [dateRange, setDateRange] = useState({ startDate: '', endDate: '' });
  const [showFilters, setShowFilters] = useState(false);
  const [dateError, setDateError] = useState('');

  const loadAllData = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      // Cargar cuentas
      const accountsResponse = await accountsService.getAccounts();
      setAccounts(accountsResponse.accounts || []);
      // Crear mapa de account_id a info de cuenta
      const accMap = {};
      (accountsResponse.accounts || []).forEach(acc => {
        accMap[acc.plaid_account_id] = acc;
      });
      setAccountsMap(accMap);
      // Cargar transacciones usando el rango de fechas
      const transactionsResponse = await transactionService.getTransactions(
        100,
        0,
        dateRange.startDate || null,
        dateRange.endDate || null
      );
      setAllTransactions(transactionsResponse.transactions || []);
      setTransactions(transactionsResponse.transactions || []);
      // Cargar resumen
      const summaryResponse = await transactionService.getTransactionSummary();
      setSummary(summaryResponse.summary || null);
    } catch (err) {
      setError(err.message || 'Error loading data');
    } finally {
      setLoading(false);
    }
  }, [dateRange.startDate, dateRange.endDate]);

  useEffect(() => {
    // Validar fechas antes de cargar datos
    if (dateRange.startDate && dateRange.endDate && dateRange.startDate > dateRange.endDate) {
      setDateError('Start date cannot be after end date');
      setTransactions([]);
      setAllTransactions([]);
      setSummary(null);
      setLoading(false);
      return;
    } else {
      setDateError('');
    }
    loadAllData();
  }, [dateRange.startDate, dateRange.endDate, loadAllData]);

  // Filtrar por ambos criterios
  const applyFilters = (type, account) => {
    let filtered = allTransactions;
    if (type && type !== 'all' && type !== 'expenses') {
      filtered = filtered.filter(tx => tx.category_primary === type);
    }
    if (type === 'expenses') {
      filtered = filtered.filter(tx => tx.category_primary !== 'INCOME' && tx.amount < 0);
    }
    if (account && account !== 'all') {
      filtered = filtered.filter(tx => tx.account_id === account);
    }
    setTransactions(filtered);
  };

  // Filtro por tipo
  const handleFilterByType = (type) => {
    setFilterType(type);
    applyFilters(type, filterAccount);
  };

  // Filtro por cuenta
  const handleFilterByAccount = (accountId) => {
    setFilterAccount(accountId);
    applyFilters(filterType, accountId);
  };

  const handleSyncTransactions = async () => {
    try {
      setSyncing(true);
      setError('');
      setSuccess('');
      const { startDate, endDate } = dateRange;
      const response = await transactionService.syncTransactions(
        startDate || null, 
        endDate || null
      );
      setSuccess(`Successfully synced ${response.synced_count || 0} transactions`);
      await loadAllData();
    } catch (err) {
      setError(err.message || 'Error syncing transactions');
    } finally {
      setSyncing(false);
    }
  };

  const handleDeleteTransaction = async (transactionId) => {
    if (!window.confirm('Are you sure you want to delete this transaction?')) {
      return;
    }
    try {
      setError('');
      setSuccess('');
      await transactionService.deleteTransaction(transactionId);
      setSuccess('Transaction deleted successfully');
      await loadAllData();
    } catch (err) {
      setError(err.message || 'Error deleting transaction');
    }
  };

  const handleDeleteAllTransactions = async () => {
    if (!window.confirm('Are you sure you want to delete ALL transactions? This action cannot be undone.')) {
      return;
    }
    try {
      setLoading(true);
      setError('');
      setSuccess('');
      await transactionService.deleteAllTransactions();
      setSuccess('All transactions deleted successfully');
      setTransactions([]);
      setSummary(null);
    } catch (err) {
      setError(err.message || 'Error deleting all transactions');
    } finally {
      setLoading(false);
    }
  };

  // Agrupar transacciones por cuenta
  const groupedTransactions = transactions.reduce((acc, tx) => {
    if (!acc[tx.account_id]) acc[tx.account_id] = [];
    acc[tx.account_id].push(tx);
    return acc;
  }, {});

  // Extraer tipos únicos de category_primary
  const transactionTypes = Array.from(
    new Set(transactions.map(tx => tx.category_primary).filter(Boolean))
  );

  // Formatear nombre de tipo (ej: FOOD_AND_DRINK -> Food And Drink)
  const formatTypeName = (type) =>
    type
      .toLowerCase()
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');

  // Filtro por cuenta
  const visibleAccountIds = filterAccount === 'all' ? Object.keys(groupedTransactions) : [filterAccount];

  const getAccountInfo = (accountId) => accountsMap[accountId] || {};

  const getTransactionIcon = (amount) => {
    return amount >= 0 ? '📈' : '📉';
  };

  // Mostrar el monto correctamente según el tipo
  const getDisplayAmount = (transaction) => {
    if (transaction.category_primary === 'INCOME') {
      return Math.abs(transaction.amount);
    }
    return transaction.amount;
  };

  // Determinar la clase de color del monto
  const getAmountClass = (transaction) => {
    if (transaction.category_primary === 'INCOME') return 'positive';
    return 'negative';
  };

  if (loading && transactions.length === 0) {
    return (
      <Layout>
        <div className="transactions-container">
          <div className="loading-spinner">Loading...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="transactions-container">
        <div className="transactions-card">
          <div className="transactions-header">
            <div className="transactions-logo">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 17V7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M3 17l4-4a2 2 0 0 1 2.83 0l2.34 2.34a2 2 0 0 0 2.83 0L21 9" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span>Billax</span>
            </div>
            <div className="transactions-title">Your Transactions</div>
            <div className="transactions-subtitle">Manage and track your financial transactions</div>
          </div>

          {error && <div className="transactions-error">{error}</div>}
          {success && <div className="transactions-success">{success}</div>}

          <div className="transactions-content">
            {/* Resumen */}
            {summary && (
              <div className="transactions-summary">
                <div className="summary-card">
                  <div className="summary-icon">📊</div>
                  <div className="summary-info">
                    <div className="summary-label">Total Transactions</div>
                    <div className="summary-value">{summary.total_count || 0}</div>
                  </div>
                </div>
                <div className="summary-card">
                  <div className="summary-icon">💰</div>
                  <div className="summary-info">
                    <div className="summary-label">Total Income</div>
                    <div className="summary-value positive">{formatCurrency(summary.total_income || 0)}</div>
                  </div>
                </div>
                <div className="summary-card">
                  <div className="summary-icon">💸</div>
                  <div className="summary-info">
                    <div className="summary-label">Total Expenses</div>
                    <div className="summary-value negative">{formatCurrency(Math.abs(summary.total_expenses || 0))}</div>
                  </div>
                </div>
                <div className="summary-card">
                  <div className="summary-icon">⚖️</div>
                  <div className="summary-info">
                    <div className="summary-label">Net Balance</div>
                    <div className={`summary-value ${(summary.net_balance || 0) >= 0 ? 'positive' : 'negative'}`}>
                      {formatCurrency(summary.net_balance || 0)}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Acciones */}
            <div className="transactions-actions">
              <Button 
                onClick={handleSyncTransactions}
                disabled={syncing}
                loading={syncing}
                className="sync-btn"
              >
                🔄 Sync Transactions
              </Button>
              <Button 
                onClick={() => setShowFilters(!showFilters)}
                className="filter-btn"
              >
                🔍 {showFilters ? 'Hide' : 'Show'} Filters
              </Button>
              <Button 
                onClick={handleDeleteAllTransactions}
                disabled={loading || transactions.length === 0}
                className="delete-all-btn"
              >
                🗑️ Delete All
              </Button>
            </div>

            {/* Filtros */}
            {showFilters && (
              <div className="transactions-filters">
                <div className="filter-section">
                  <label>Date Range:</label>
                  <div className="date-inputs">
                    <input
                      type="date"
                      value={dateRange.startDate}
                      onChange={(e) => setDateRange({...dateRange, startDate: e.target.value})}
                      placeholder="Start Date"
                      max={dateRange.endDate || undefined}
                    />
                    <input
                      type="date"
                      value={dateRange.endDate}
                      onChange={(e) => setDateRange({...dateRange, endDate: e.target.value})}
                      placeholder="End Date"
                      min={dateRange.startDate || undefined}
                    />
                  </div>
                  {dateError && <div style={{ color: '#e74c3c', marginTop: 4 }}>{dateError}</div>}
                </div>
                <div className="filter-section">
                  <label>Filter by Type:</label>
                  <div className="type-filters">
                    {filterType === 'all' && (
                      <>
                        <button className="type-filter active">All</button>
                        {transactionTypes.map(type => (
                          <button key={type} className="type-filter" onClick={() => handleFilterByType(type)}>
                            {formatTypeName(type)}
                          </button>
                        ))}
                      </>
                    )}
                    {filterType === 'expenses' && (
                      <>
                        <button className="type-filter" onClick={() => handleFilterByType('all')}>All</button>
                        <button className="type-filter active">Expenses</button>
                      </>
                    )}
                    {filterType !== 'all' && filterType !== 'expenses' && (
                      <>
                        <button className="type-filter" onClick={() => handleFilterByType('all')}>All</button>
                        <button className="type-filter active">{formatTypeName(filterType)}</button>
                      </>
                    )}
                  </div>
                </div>
                <div className="filter-section">
                  <label>Filter by Account:</label>
                  <div className="type-filters">
                    <button
                      className={`type-filter ${filterAccount === 'all' ? 'active' : ''}`}
                      onClick={() => handleFilterByAccount('all')}
                    >
                      All Accounts
                    </button>
                    {accounts.map(acc => (
                      <button
                        key={acc.plaid_account_id}
                        className={`type-filter ${filterAccount === acc.plaid_account_id ? 'active' : ''}`}
                        onClick={() => handleFilterByAccount(acc.plaid_account_id)}
                      >
                        {getAccountIcon(acc.type)} {acc.name}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Lista de transacciones agrupadas por cuenta */}
            {transactions.length === 0 && !loading && !dateError && (
              <div style={{ textAlign: 'center', color: '#888', margin: '2rem 0' }}>
                No transactions found for the selected date range.
              </div>
            )}
            {visibleAccountIds.map(accountId => {
              const accInfo = getAccountInfo(accountId);
              const txs = groupedTransactions[accountId] || [];
              if (txs.length === 0) return null;
              return (
                <div key={accountId} className="transactions-account-group">
                  <div className="account-group-header">
                    <span className="account-group-icon">{getAccountIcon(accInfo.type)}</span>
                    <span className="account-group-name">{accInfo.name || accountId}</span>
                    <span className="account-group-type">{accInfo.type} {accInfo.subtype ? `• ${accInfo.subtype}` : ''}</span>
                  </div>
                  <div className="transactions-grid">
                    {txs.map((transaction) => (
                      <div key={transaction.id} className="transaction-card" style={{ display: 'flex', alignItems: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                          <div className="transaction-header">
                            <div className="transaction-icon">
                              {transaction.logo_url ? (
                                <img src={transaction.logo_url} alt="merchant logo" style={{ width: 32, height: 32, borderRadius: '50%' }} />
                              ) : (
                                getTransactionIcon(transaction.amount)
                              )}
                            </div>
                            <div className="transaction-amount">
                              <span className={getAmountClass(transaction)}>
                                {formatCurrency(getDisplayAmount(transaction))}
                              </span>
                            </div>
                          </div>
                          <div className="transaction-details" style={{ marginLeft: 16 }}>
                            <div className="transaction-description">
                              {transaction.merchant_name || transaction.name || 'No description'}
                            </div>
                            <div className="transaction-account-name" style={{ color: '#888', fontSize: 13, marginBottom: 2 }}>
                              {getAccountInfo(transaction.account_id).name || transaction.account_id}
                            </div>
                            <div className="transaction-date">
                              {formatDate(transaction.date)}
                              {transaction.authorized_date && (
                                <span style={{ marginLeft: 8, color: '#888', fontSize: 12 }}>
                                  (Auth: {formatDate(transaction.authorized_date)})
                                </span>
                              )}
                            </div>
                            {transaction.category_primary && (
                              <div className="transaction-type">
                                {transaction.category_primary} {transaction.category_detailed ? `• ${transaction.category_detailed}` : ''}
                              </div>
                            )}
                            {transaction.payment_channel && (
                              <div className="transaction-type">
                                Channel: {transaction.payment_channel}
                              </div>
                            )}
                            {transaction.website && (
                              <div className="transaction-type">
                                <a href={`https://${transaction.website}`} target="_blank" rel="noopener noreferrer">Visit website</a>
                              </div>
                            )}
                            {transaction.pending && (
                              <div className="transaction-type" style={{ color: '#e67e22' }}>
                                Pending
                              </div>
                            )}
                          </div>
                        </div>
                        <button 
                          onClick={() => handleDeleteTransaction(transaction.id)}
                          className="delete-transaction-btn"
                          title="Delete transaction"
                          style={{ marginLeft: 'auto' }}
                        >
                          🗑️
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default Transactions; 