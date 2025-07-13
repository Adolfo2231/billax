import React, { useState, useEffect, useCallback } from 'react';
import Button from '../Button';
import Input from '../Input';

const GoalCard = ({ goal, onEdit, onDelete, onProgressInputChange, onProgressTypeChange, onProgressUpdateClick, progressInput, progressType, formatCurrency, accounts, goals }) => {
  const [progressError, setProgressError] = useState('');

  const getLinkedAccountAvailable = useCallback(() => {
    if (!goal.linked_account_id) return null;
    const account = accounts.find(a => String(a.id) === String(goal.linked_account_id));
    if (!account) return null;
    
    // Calcular el total reservado por todas las metas que usan esta cuenta
    const totalReserved = goals
      .filter(g => g.linked_account_id && String(g.linked_account_id) === String(goal.linked_account_id))
      .reduce((sum, g) => sum + (parseFloat(g.linked_amount) || 0), 0);
    
    const balance = account.balances?.available ?? account.available_balance ?? 0;
    return balance - totalReserved;
  }, [goal.linked_account_id, accounts, goals]);

  useEffect(() => {
    if (progressType === 'linked' && progressInput && goal.linked_account_id) {
      const available = getLinkedAccountAvailable();
      if (available !== null && parseFloat(progressInput) > parseFloat(available)) {
        setProgressError(`Cannot exceed available balance: ${formatCurrency(available)}`);
      } else {
        setProgressError('');
      }
    } else {
      setProgressError('');
    }
  }, [progressInput, progressType, goal.linked_account_id, accounts, goals, formatCurrency, getLinkedAccountAvailable]);

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'savings': return '💰';
      case 'investment': return '📈';
      case 'debt': return '💳';
      case 'emergency': return '🚨';
      case 'vacation': return '✈️';
      case 'education': return '🎓';
      default: return '🎯';
    }
  };

  const handleProgressUpdate = () => {
    if (progressError) return;
    onProgressUpdateClick(goal.id);
  };

  return (
    <div className={`goal-card ${goal.status}`}>
      <div className="goal-header">
        <div className="goal-title">
          <span className="category-icon">{getCategoryIcon(goal.category)}</span>
          <h3>{goal.title}</h3>
        </div>
        <div className="goal-actions">
          <Button size="small" onClick={() => onEdit(goal)}>Edit</Button>
          <button className="icon-btn delete-btn" title="Delete goal" onClick={() => onDelete(goal.id)}>
            🗑️
          </button>
        </div>
      </div>
      {goal.description && <p className="goal-description">{goal.description}</p>}
      {goal.linked_account && (
        <div className="goal-linked-account">
          <span className="linked-account-label">Linked Account:</span>
          <span className="linked-account-name">{goal.linked_account.name}</span>
          {goal.linked_amount && (
            <span className="linked-account-amount">({formatCurrency(goal.linked_amount)})</span>
          )}
          {(() => {
            const available = getLinkedAccountAvailable();
            return available !== null ? (
              <span className="linked-account-available" style={{ color: '#666', fontSize: '0.9em' }}>
                Available: {formatCurrency(available)}
              </span>
            ) : null;
          })()}
        </div>
      )}
      <div className="goal-progress">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${goal.progress_percentage}%` }}></div>
        </div>
        <div className="progress-text">
          {formatCurrency((goal.current_amount || 0) + (goal.linked_amount || 0))} / {formatCurrency(goal.target_amount)}
          <span className="progress-percentage">({Number(goal.progress_percentage || 0).toFixed(1)}%)</span>
        </div>
        <div className="progress-breakdown">
          <span>{formatCurrency(goal.current_amount || 0)} manual</span>
          {goal.linked_amount ? <span> + {formatCurrency(goal.linked_amount)} linked</span> : null}
        </div>
      </div>
      <div className="goal-details">
        <div className="goal-info">
          <span className={`status-badge ${goal.status}`}>{goal.status}</span>
          {goal.deadline && (
            <span className="deadline">
              Due: {new Date(goal.deadline).toLocaleDateString()}
              {goal.days_remaining !== null && (
                <span className={`days-remaining ${goal.days_remaining < 0 ? 'overdue' : ''}`}>
                  {goal.days_remaining < 0 ? `${Math.abs(goal.days_remaining)} days overdue` : `${goal.days_remaining} days left`}
                </span>
              )}
            </span>
          )}
        </div>
        {goal.status === 'active' && (
          <div className="progress-update">
            <Input
              type="number"
              placeholder="Add amount"
              min="0"
              step="0.01"
              value={progressInput || ''}
              onChange={(name, value) => onProgressInputChange(goal.id, value)}
              name={`progress_${goal.id}`}
            />
            {goal.linked_account ? (
              <>
                <select
                  value={progressType || 'manual'}
                  onChange={e => onProgressTypeChange(goal.id, e.target.value)}
                  style={{ marginTop: 8, marginRight: 8 }}
                >
                  <option value="manual">Manual / Cash</option>
                  <option value="linked">From Linked Account</option>
                </select>
                {progressType === 'linked' && (() => {
                  const available = getLinkedAccountAvailable();
                  return available !== null ? (
                    <div style={{ fontSize: '0.85em', color: '#666', marginTop: 4 }}>
                      Available: {formatCurrency(available)}
                    </div>
                  ) : null;
                })()}
              </>
            ) : null}
            <Button 
              size="small" 
              style={{ marginTop: 8 }} 
              onClick={handleProgressUpdate}
              disabled={!!progressError}
            >
              Add
            </Button>
            {progressError && (
              <div style={{ color: '#d32f2f', fontSize: '0.85em', marginTop: 4 }}>
                {progressError}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default GoalCard;
