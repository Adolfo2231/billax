import React, { useState, useEffect, useCallback } from 'react';
import Layout from '../components/Layout';
import Button from '../components/Button';
import Input from '../components/Input';
import goalService from '../services/goalService';
import accountsService from '../services/accountsService';
import { formatCurrency } from '../utils/format';
import './Goals.css';
import GoalsSummary from '../components/goals/GoalsSummary';
import GoalCard from '../components/goals/GoalCard';
import GoalFormModal from '../components/goals/GoalFormModal';

function Goals() {
    const [goals, setGoals] = useState([]);
    const [summary, setSummary] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showForm, setShowForm] = useState(false);
    const [editingGoal, setEditingGoal] = useState(null);
    const [categories, setCategories] = useState([]);
    const [accounts, setAccounts] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [searchFilters, setSearchFilters] = useState({
        status: '',
        category: '',
        minAmount: '',
        maxAmount: ''
    });

    const [formData, setFormData] = useState({
        title: '',
        target_amount: '',
        description: '',
        deadline: '',
        category: '',
        linked_account_id: '',
        linked_amount: ''
    });
    const [linkedAmountError, setLinkedAmountError] = useState('');
    const [progressInputs, setProgressInputs] = useState({});
    const [progressTypes, setProgressTypes] = useState({});

    useEffect(() => {
        loadGoals();
        loadCategories();
        loadAccounts();
    }, []);

    const loadGoals = async () => {
        try {
            setLoading(true);
            const [goalsData, summaryData] = await Promise.all([
                goalService.getGoals(),
                goalService.getGoalsSummary()
            ]);
            setGoals(goalsData);
            setSummary(summaryData);
        } catch (err) {
            setError('Error loading goals');
            console.error('Error loading goals:', err);
        } finally {
            setLoading(false);
        }
    };

    const loadCategories = async () => {
        try {
            const categoriesData = await goalService.getGoalCategories();
            setCategories(categoriesData);
        } catch (err) {
            console.error('Error loading categories:', err);
        }
    };

    const loadAccounts = async () => {
        try {
            const accountsData = await accountsService.getAccounts();
            setAccounts(accountsData.accounts || []);
        } catch (err) {
            console.error('Error loading accounts:', err);
        }
    };

    const handleSearch = async () => {
        try {
            setLoading(true);
            const searchParams = {
                searchTerm: searchTerm || null,
                status: searchFilters.status || null,
                category: searchFilters.category || null,
                minAmount: searchFilters.minAmount ? parseFloat(searchFilters.minAmount) : null,
                maxAmount: searchFilters.maxAmount ? parseFloat(searchFilters.maxAmount) : null
            };
            
            const goalsData = await goalService.searchGoals(
                searchParams.searchTerm,
                searchParams.status,
                searchParams.category,
                searchParams.minAmount,
                searchParams.maxAmount
            );
            setGoals(goalsData);
        } catch (err) {
            setError('Error searching goals');
            console.error('Error searching goals:', err);
        } finally {
            setLoading(false);
        }
    };

    const clearSearch = () => {
        setSearchTerm('');
        setSearchFilters({
            status: '',
            category: '',
            minAmount: '',
            maxAmount: ''
        });
        loadGoals();
    };

    const handleSubmit = async (e) => {
        if (!e || !e.preventDefault) return;
        e.preventDefault();
        try {
            const dataToSend = {
                ...formData,
                target_amount: parseFloat(formData.target_amount) || 0,
                linked_account_id: formData.linked_account_id ? parseInt(formData.linked_account_id, 10) : null,
                linked_amount: formData.linked_amount ? parseFloat(formData.linked_amount) : null,
            };
            if (editingGoal) {
                await goalService.updateGoal(editingGoal.id, dataToSend);
            } else {
                await goalService.createGoal(dataToSend);
            }
            resetForm();
            loadGoals();
        } catch (err) {
            setError('Error saving goal');
            console.error('Error saving goal:', err);
        }
    };

    const handleEdit = (goal) => {
        setEditingGoal(goal);
        setFormData({
            title: goal.title,
            target_amount: goal.target_amount.toString(),
            description: goal.description || '',
            deadline: goal.deadline || '',
            category: goal.category || '',
            linked_account_id: goal.linked_account_id || '',
            linked_amount: goal.linked_amount ? goal.linked_amount.toString() : ''
        });
        setShowForm(true);
    };

    const handleDelete = async (goalId) => {
        if (window.confirm('Are you sure you want to delete this goal?')) {
            try {
                await goalService.deleteGoal(goalId);
                loadGoals();
            } catch (err) {
                setError('Error deleting goal');
                console.error('Error deleting goal:', err);
            }
        }
    };

    const handleProgressInputChange = (goalId, value) => {
        setProgressInputs((prev) => ({ ...prev, [goalId]: value }));
    };

    const handleProgressTypeChange = (goalId, value) => {
        setProgressTypes((prev) => ({ ...prev, [goalId]: value }));
    };

    const handleUpdateProgress = async (goalId, amount, type = 'manual') => {
        try {
            await goalService.updateProgress(goalId, parseFloat(amount), type);
            loadGoals();
        } catch (err) {
            setError('Error updating progress');
            console.error('Error updating progress:', err);
        }
    };

    const handleProgressUpdateClick = (goalId) => {
        const amount = progressInputs[goalId];
        const type = progressTypes[goalId] || 'manual';
        if (amount > 0) {
            handleUpdateProgress(goalId, amount, type);
            setProgressInputs((prev) => ({ ...prev, [goalId]: '' }));
        }
    };

    const resetForm = () => {
        setFormData({
            title: '',
            target_amount: '',
            description: '',
            deadline: '',
            category: '',
            linked_account_id: '',
            linked_amount: ''
        });
        setEditingGoal(null);
        setShowForm(false);
    };

    const getFilteredGoals = () => {
        if (searchFilters.status === 'all') return goals;
        if (searchFilters.status === 'active') return goals.filter(g => g.status === 'active');
        if (searchFilters.status === 'completed') return goals.filter(g => g.status === 'completed');
        if (searchFilters.status === 'overdue') return goals.filter(g => g.days_remaining < 0 && g.status === 'active');
        return goals;
    };

    const getSelectedAccountAvailable = useCallback(() => {
        if (!formData.linked_account_id) return null;
        const account = accounts.find(a => String(a.id) === String(formData.linked_account_id));
        if (!account) return null;
        return account.balances?.available ?? account.available_balance ?? null;
    }, [formData.linked_account_id, accounts]);

    useEffect(() => {
        if (formData.linked_account_id && formData.linked_amount) {
            const available = getSelectedAccountAvailable();
            const inputAmount = parseFloat(formData.linked_amount);
            if (available !== null && inputAmount > available) {
                setLinkedAmountError(`Cannot exceed available balance: $${Number(available).toLocaleString()}`);
            } else {
                setLinkedAmountError('');
            }
        } else {
            setLinkedAmountError('');
        }
    }, [formData.linked_account_id, formData.linked_amount, accounts, getSelectedAccountAvailable]);

    if (loading) {
        return (
            <Layout>
                <div className="goals-container">
                    <div className="loading">Loading goals...</div>
                </div>
            </Layout>
        );
    }

    return (
        <Layout>
            <div className="goals-container">
                <div className="goals-header">
                    <h1>Financial Goals</h1>
                    <Button onClick={() => setShowForm(true)}>
                        + New Goal
                    </Button>
                </div>

                {error && (
                    <div className="error-message">
                        {error}
                        <button onClick={() => setError(null)}>×</button>
                    </div>
                )}

                <GoalsSummary summary={summary} />

                {/* Search Section */}
                <div className="search-section">
                    <div className="search-header">
                        <h3>Search Goals</h3>
                        <Button size="small" onClick={clearSearch}>Clear Search</Button>
                    </div>
                    <div className="search-form">
                        <div className="search-row">
                            <Input
                                type="text"
                                placeholder="Search by title or description..."
                                value={searchTerm}
                                onChange={(name, value) => setSearchTerm(value)}
                                name="searchTerm"
                            />
                            <Button onClick={handleSearch}>Search</Button>
                        </div>
                        <div className="search-filters">
                            <select
                                value={searchFilters.status}
                                onChange={e => setSearchFilters({...searchFilters, status: e.target.value})}
                            >
                                <option value="">All Status</option>
                                <option value="active">Active</option>
                                <option value="completed">Completed</option>
                                <option value="cancelled">Cancelled</option>
                            </select>
                            <select
                                value={searchFilters.category}
                                onChange={e => setSearchFilters({...searchFilters, category: e.target.value})}
                            >
                                <option value="">All Categories</option>
                                {categories.map(cat => (
                                    <option key={cat.value} value={cat.value}>
                                        {cat.label}
                                    </option>
                                ))}
                            </select>
                            <Input
                                type="number"
                                placeholder="Min Amount"
                                value={searchFilters.minAmount}
                                onChange={(name, value) => setSearchFilters({...searchFilters, minAmount: value})}
                                name="minAmount"
                                min="0"
                                step="0.01"
                            />
                            <Input
                                type="number"
                                placeholder="Max Amount"
                                value={searchFilters.maxAmount}
                                onChange={(name, value) => setSearchFilters({...searchFilters, maxAmount: value})}
                                name="maxAmount"
                                min="0"
                                step="0.01"
                            />
                        </div>
                    </div>
                </div>

                <div className="goals-list">
                    {getFilteredGoals().length === 0 ? (
                        <div className="no-goals">
                            <p>No goals found. Create your first financial goal!</p>
                        </div>
                    ) : (
                        getFilteredGoals().map(goal => (
                            <GoalCard
                                key={goal.id}
                                goal={goal}
                                onEdit={handleEdit}
                                onDelete={handleDelete}
                                onProgressInputChange={handleProgressInputChange}
                                onProgressTypeChange={handleProgressTypeChange}
                                onProgressUpdateClick={handleProgressUpdateClick}
                                progressInput={progressInputs[goal.id]}
                                progressType={progressTypes[goal.id]}
                                formatCurrency={formatCurrency}
                                accounts={accounts}
                                goals={goals}
                            />
                        ))
                    )}
                </div>

                {showForm && (
                    <GoalFormModal
                        formData={formData}
                        setFormData={setFormData}
                        onSubmit={handleSubmit}
                        onCancel={resetForm}
                        categories={categories}
                        accounts={accounts}
                        editingGoal={editingGoal}
                        loading={loading}
                        error={error}
                        linkedAmountError={linkedAmountError}
                        goals={goals}
                    />
                )}
            </div>
        </Layout>
    );
}

export default Goals; 