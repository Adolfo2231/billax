import React, { useState, useEffect, useRef } from 'react';
import chatService from '../services/chatService';
import accountsService from '../services/accountsService';
import './FloatingChat.css';

function FloatingChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [showAccountSelector, setShowAccountSelector] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      loadChatHistory();
      loadAccounts();
    }
  }, [isOpen]);

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
      console.error('Error loading accounts:', err);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    try {
      setSending(true);
      setError('');
      const response = await chatService.sendMessage(input.trim(), selectedAccount?.id);
      setMessages((prev) => [
        ...prev,
        { 
          id: Date.now(), 
          message: input.trim(), 
          response: response.response, 
          created_at: new Date().toISOString(),
          account: selectedAccount
        }
      ]);
      setInput('');
    } catch (err) {
      setError(err.message || 'Error sending message');
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  const handleAccountSelect = (account) => {
    setSelectedAccount(account);
    setShowAccountSelector(false);
    // Agregar un mensaje del sistema indicando la cuenta seleccionada
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        message: `Cuenta seleccionada: ${account.name} (${account.mask})`,
        response: `Perfecto! Ahora puedes hacer preguntas específicas sobre tu cuenta ${account.name}. ¿En qué puedo ayudarte?`,
        created_at: new Date().toISOString(),
        isSystemMessage: true
      }
    ]);
  };

  const clearSelectedAccount = () => {
    setSelectedAccount(null);
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        message: 'Cuenta deseleccionada',
        response: 'Ahora puedes hacer preguntas generales sobre tus finanzas.',
        created_at: new Date().toISOString(),
        isSystemMessage: true
      }
    ]);
  };

  return (
    <>
      {/* Floating Button */}
      <button 
        className="floating-chat-button"
        onClick={() => setIsOpen(!isOpen)}
        title="Chat with AI"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>

      {/* Chat Modal */}
      {isOpen && (
        <div className="floating-chat-overlay" onClick={() => setIsOpen(false)}>
          <div className="floating-chat-modal" onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className="floating-chat-header">
              <div className="floating-chat-title">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <span>AI Assistant</span>
              </div>
              <button 
                className="floating-chat-close"
                onClick={() => setIsOpen(false)}
              >
                ×
              </button>
            </div>

            {/* Account Selector */}
            <div className="floating-chat-account-section">
              <div className="floating-chat-account-header">
                <button 
                  className="floating-chat-account-btn"
                  onClick={() => setShowAccountSelector(!showAccountSelector)}
                >
                  {selectedAccount ? (
                    <>
                      <span>📊 {selectedAccount.name} ({selectedAccount.mask})</span>
                      <span 
                        className="floating-chat-clear-account"
                        onClick={e => {
                          e.stopPropagation();
                          clearSelectedAccount();
                        }}
                        title="Deseleccionar cuenta"
                        style={{ marginLeft: 8, cursor: 'pointer', fontWeight: 'bold', fontSize: 18 }}
                        role="button"
                        tabIndex={0}
                        onKeyPress={e => { if (e.key === 'Enter' || e.key === ' ') { e.stopPropagation(); clearSelectedAccount(); } }}
                      >
                        ×
                      </span>
                    </>
                  ) : (
                    <span>🏦 Seleccionar cuenta</span>
                  )}
                  <span className="floating-chat-account-arrow">
                    {showAccountSelector ? '▲' : '▼'}
                  </span>
                </button>
              </div>
              
              {showAccountSelector && (
                <div className="floating-chat-accounts-list">
                  {accounts.length === 0 ? (
                    <div className="floating-chat-no-accounts">
                      No hay cuentas disponibles
                    </div>
                  ) : (
                    accounts.map((account) => (
                      <button
                        key={account.id}
                        className="floating-chat-account-item"
                        onClick={() => handleAccountSelect(account)}
                      >
                        <div className="floating-chat-account-info">
                          <strong>{account.name}</strong>
                          <span>{account.mask}</span>
                        </div>
                        <div className="floating-chat-account-balance">
                          ${account.balances?.current || 0}
                        </div>
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>

            {/* Messages */}
            <div className="floating-chat-messages">
              {error && <div className="floating-chat-error">{error}</div>}
              
              {loading ? (
                <div className="floating-chat-loading">Loading...</div>
              ) : messages.length === 0 ? (
                <div className="floating-chat-empty">
                  <p>👋 Hi! I'm your AI financial assistant.</p>
                  <p>Select an account above to ask specific questions, or ask me anything about your finances!</p>
                </div>
              ) : (
                messages.map((msg) => (
                  <div key={msg.id} className={`floating-chat-message ${msg.isSystemMessage ? 'floating-chat-system-message' : ''}`}>
                    <div className="floating-chat-user-message">
                      <strong>You:</strong>{' '}
                      {msg.message.split('\n').map((line, idx) => (
                        <span key={idx}>
                          {line}
                          <br />
                        </span>
                      ))}
                    </div>
                    <div className="floating-chat-ai-message">
                      <strong>AI:</strong>{' '}
                      {msg.response.split('\n').map((line, idx) => (
                        <span key={idx}>
                          {line}
                          <br />
                        </span>
                      ))}
                    </div>
                    <div className="floating-chat-timestamp">
                      {msg.created_at && new Date(msg.created_at).toLocaleString()}
                    </div>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSend} className="floating-chat-input-form">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={selectedAccount ? `Ask about ${selectedAccount.name}...` : "Type your message..."}
                className="floating-chat-input"
                disabled={sending}
                autoFocus
              />
              <button 
                type="submit" 
                className="floating-chat-send"
                disabled={sending || !input.trim()}
              >
                {sending ? '...' : 'Send'}
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

export default FloatingChat; 