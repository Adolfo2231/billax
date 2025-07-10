import React, { useState, useEffect, useRef } from 'react';
import Button from '../components/Button';
import Layout from '../components/Layout';
import chatService from '../services/chatService';
import accountsService from '../services/accountsService';
import './Transactions.css';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [sending, setSending] = useState(false);
  const [deletingAll, setDeletingAll] = useState(false);
  const messagesEndRef = useRef(null);
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [showAccountFilters, setShowAccountFilters] = useState(false);

  useEffect(() => {
    loadChatHistory();
    loadAccounts();
  }, []);

  useEffect(() => {
    // Scroll to bottom on new message
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const loadChatHistory = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await chatService.getChatHistory();
      setMessages(response.history || []);
    } catch (err) {
      setError(err.message || 'Error loading chat history');
    } finally {
      setLoading(false);
    }
  };

  const loadAccounts = async () => {
    try {
      const response = await accountsService.getAccounts();
      setAccounts(response.accounts || []);
    } catch (err) {
      // Opcional: setError(err.message || 'Error loading accounts');
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    try {
      setSending(true);
      setError('');
      setSuccess('');
      const response = await chatService.sendMessage(input.trim(), selectedAccount?.id);
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), message: input.trim(), response: response.response, created_at: new Date().toISOString() }
      ]);
      setInput('');
      setSuccess('Message sent!');
    } catch (err) {
      setError(err.message || 'Error sending message');
    } finally {
      setSending(false);
    }
  };

  const handleDelete = async (chatId) => {
    if (!window.confirm('Are you sure you want to delete this message?')) return;
    try {
      setError('');
      await chatService.deleteChat(chatId);
      setMessages((prev) => prev.filter((msg) => msg.id !== chatId));
    } catch (err) {
      setError(err.message || 'Error deleting message');
    }
  };

  const handleDeleteAll = async () => {
    if (!window.confirm('Are you sure you want to delete ALL chat history?')) return;
    try {
      setDeletingAll(true);
      setError('');
      await chatService.deleteAllChats();
      setMessages([]);
      setSuccess('All chat history deleted');
    } catch (err) {
      setError(err.message || 'Error deleting all chat history');
    } finally {
      setDeletingAll(false);
    }
  };

  // Obtener el icono de la cuenta
  const getAccountIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'depository': return '🏦';
      case 'credit': return '💳';
      case 'loan': return '💰';
      case 'investment': return '📈';
      default: return '🏛️';
    }
  };

  return (
    <Layout>
      <div className="transactions-container">
        <div className="transactions-card">
          {/* Botón para mostrar filtros de cuenta */}
          <div style={{ marginBottom: 16 }}>
            <Button
              className="filter-btn"
              type="button"
              onClick={() => setShowAccountFilters((prev) => !prev)}
            >
              {showAccountFilters ? 'Hide Account Filter' : 'Filter by Account'}
            </Button>
          </div>
          {/* Selector de cuenta estilo filtro, solo si showAccountFilters está activo */}
          {showAccountFilters && (
            <div style={{ marginBottom: 16 }}>
              <span style={{ fontWeight: 600, marginRight: 8 }}>Cuenta:</span>
              <div className="type-filters" style={{ flexWrap: 'wrap', gap: 8 }}>
                <button
                  className={`type-filter${!selectedAccount ? ' active' : ''}`}
                  onClick={() => setSelectedAccount(null)}
                  style={{ minWidth: 120 }}
                >
                  All Accounts
                </button>
                {accounts.map(acc => (
                  <button
                    key={acc.id}
                    className={`type-filter${selectedAccount && selectedAccount.id === acc.id ? ' active' : ''}`}
                    onClick={() => setSelectedAccount(acc)}
                    style={{ minWidth: 120, display: 'flex', alignItems: 'center', gap: 6 }}
                  >
                    <span>{getAccountIcon(acc.type)}</span> {acc.name}
                  </button>
                ))}
              </div>
            </div>
          )}
          <div className="transactions-header">
            <div className="transactions-logo">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 17V7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M3 17l4-4a2 2 0 0 1 2.83 0l2.34 2.34a2 2 0 0 0 2.83 0L21 9" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span>Billax</span>
            </div>
            <div className="transactions-title">AI Chat</div>
            <div className="transactions-subtitle">Ask anything about your finances</div>
          </div>

          {error && <div className="transactions-error">{error}</div>}
          {success && <div className="transactions-success">{success}</div>}

          <div className="transactions-actions" style={{ marginBottom: 16 }}>
            <Button onClick={handleDeleteAll} disabled={deletingAll || messages.length === 0} className="delete-all-btn">
              🗑️ Delete All
            </Button>
          </div>

          <div className="transactions-content" style={{ minHeight: 300, maxHeight: 400, overflowY: 'auto', marginBottom: 16 }}>
            {loading ? (
              <div className="loading-spinner">Loading...</div>
            ) : messages.length === 0 ? (
              <div style={{ textAlign: 'center', color: '#888', margin: '2rem 0' }}>
                No chat history yet.
              </div>
            ) : (
              <div className="chat-bubbles-container" style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
                {messages.map((msg) => (
                  <div key={msg.id} style={{ marginBottom: 8 }}>
                    {/* Usuario */}
                    <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <div style={{
                        background: 'linear-gradient(90deg, #b2f7c1 0%, #e0ffe6 100%)',
                        color: '#222',
                        borderRadius: '18px 18px 4px 18px',
                        padding: '12px 18px',
                        maxWidth: '70%',
                        fontSize: 16,
                        wordBreak: 'break-word',
                        boxShadow: '0 2px 8px rgba(56,239,125,0.08)'
                      }}>
                        {msg.message}
                        <div style={{ fontSize: 11, color: '#888', marginTop: 4, textAlign: 'right' }}>
                          {msg.created_at && new Date(msg.created_at).toLocaleString()}
                        </div>
                      </div>
                    </div>
                    {/* IA */}
                    <div style={{ display: 'flex', justifyContent: 'flex-start', marginTop: 6 }}>
                      <div style={{
                        background: 'linear-gradient(90deg, #f0f0f0 0%, #e6e6e6 100%)',
                        color: '#222',
                        borderRadius: '18px 18px 18px 4px',
                        padding: '12px 18px',
                        maxWidth: '70%',
                        fontSize: 16,
                        wordBreak: 'break-word',
                        boxShadow: '0 2px 8px rgba(56,239,125,0.04)',
                        whiteSpace: 'pre-line'
                      }}>
                        {msg.response.split('\n').map((line, idx) => (
                          <span key={idx}>
                            {line}
                            {idx < msg.response.split('\n').length - 1 && <br />}
                          </span>
                        ))}
                      </div>
                      <button
                        onClick={() => handleDelete(msg.id)}
                        className="delete-transaction-btn"
                        title="Delete message"
                        style={{ marginLeft: 8, alignSelf: 'center' }}
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          <form onSubmit={handleSend} style={{ display: 'flex', gap: 8 }}>
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Type your message..."
              className="input-group"
              style={{ flex: 1, minWidth: 0 }}
              disabled={sending}
              autoFocus
            />
            <Button type="submit" className="sync-btn" disabled={sending || !input.trim()} loading={sending}>
              Send
            </Button>
          </form>
        </div>
      </div>
    </Layout>
  );
}

export default Chat; 