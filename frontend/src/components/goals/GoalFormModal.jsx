import React from 'react';
import Button from '../Button';
import Input from '../Input';

const GoalFormModal = ({
  formData,
  setFormData,
  onSubmit,
  onCancel,
  categories = [],
  accounts = [],
  editingGoal,
  loading,
  error,
  linkedAmountError,
  goals = []
}) => {
  // Helper para mostrar saldo disponible (corrige para edición)
  const getSelectedAccountAvailable = () => {
    if (!formData.linked_account_id) return null;
    const acc = accounts.find(a => String(a.id) === String(formData.linked_account_id));
    if (!acc) return null;
    // Calcular el total reservado por otras metas (excluyendo la actual si es edición)
    const currentGoalId = editingGoal ? editingGoal.id : null;
    const totalReserved = goals
      .filter(g => g.linked_account_id && String(g.linked_account_id) === String(formData.linked_account_id) && g.id !== currentGoalId)
      .reduce((sum, g) => sum + (parseFloat(g.linked_amount) || 0), 0);
    const accountAvailable = acc.balances?.available ?? acc.available_balance ?? 0;
    return accountAvailable - totalReserved;
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h2>{editingGoal ? 'Edit Goal' : 'Create New Goal'}</h2>
          <button onClick={onCancel} className="close-btn">×</button>
        </div>
        <form onSubmit={onSubmit} className="goal-form">
          <div className="form-group">
            <label>Title *</label>
            <Input
              type="text"
              value={formData.title}
              onChange={(name, value) => setFormData({ ...formData, [name]: value })}
              name="title"
              required
            />
          </div>

          <div className="form-group">
            <label>Target Amount *</label>
            <Input
              type="number"
              value={formData.target_amount}
              onChange={(name, value) => setFormData({ ...formData, [name]: value })}
              name="target_amount"
              min="0"
              step="0.01"
              required
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              value={formData.description}
              onChange={e => setFormData({ ...formData, description: e.target.value })}
              rows="3"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Category</label>
              <select
                value={formData.category}
                onChange={e => setFormData({ ...formData, category: e.target.value })}
              >
                <option value="">Select category</option>
                {categories.map(cat => (
                  <option key={cat.value} value={cat.value}>{cat.label}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Linked Account</label>
              <select
                value={formData.linked_account_id}
                onChange={e => setFormData({ ...formData, linked_account_id: e.target.value })}
              >
                <option value="">No Account Linked</option>
                {accounts.map(account => (
                  <option key={account.id} value={account.id}>{account.name}</option>
                ))}
              </select>
            </div>
          </div>

          {formData.linked_account_id && (
            <div className="form-group">
              <label>Linked Amount {(() => {
                const available = getSelectedAccountAvailable();
                return available !== null ? <span style={{ color: '#888', fontWeight: 400, fontSize: '0.95em' }}> (Available: ${Number(available).toLocaleString()})</span> : null;
              })()}</label>
              <Input
                type="number"
                value={formData.linked_amount}
                onChange={(name, value) => setFormData({ ...formData, [name]: value })}
                name="linked_amount"
                min="0"
                step="0.01"
                placeholder="Amount to link"
              />
              {/* Validación visual: no permitir reservar más de lo disponible */}
              {(() => {
                const available = getSelectedAccountAvailable();
                if (
                  available !== null &&
                  formData.linked_amount &&
                  parseFloat(formData.linked_amount) > available
                ) {
                  return <div style={{ color: '#d32f2f', fontSize: '0.95em', marginTop: 4 }}>Cannot reserve more than available: ${Number(available).toLocaleString()}</div>;
                }
                return linkedAmountError && <div style={{ color: '#d32f2f', fontSize: '0.95em', marginTop: 4 }}>{linkedAmountError}</div>;
              })()}
            </div>
          )}

          <div className="form-row">
            <div className="form-group">
              <label>Deadline</label>
              <Input
                type="date"
                value={formData.deadline}
                onChange={(name, value) => setFormData({ ...formData, [name]: value })}
                name="deadline"
              />
            </div>
          </div>

          {error && (
            <div className="error-message">
              {error}
              <button onClick={onCancel}>×</button>
            </div>
          )}

          <div className="form-actions">
            <Button type="submit" disabled={!!linkedAmountError || loading || (formData.linked_account_id && formData.linked_amount && parseFloat(formData.linked_amount) > getSelectedAccountAvailable())}>
              {editingGoal ? 'Update Goal' : 'Create Goal'}
            </Button>
            <Button type="button" variant="secondary" onClick={onCancel}>
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default GoalFormModal; 