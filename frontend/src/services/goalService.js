import api from './api';

class GoalService {
    /**
     * Get all goals for the authenticated user
     * @param {string} status - Optional filter by status
     * @param {string} category - Optional filter by category
     * @returns {Promise<Array>} Array of goals
     */
    async getGoals(status = null, category = null) {
        try {
            const params = new URLSearchParams();
            if (status) params.append('status', status);
            if (category) params.append('category', category);
            
            const response = await api.get(`/goals/?${params.toString()}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching goals:', error);
            throw error;
        }
    }

    /**
     * Create a new goal
     * @param {Object} goalData - Goal data
     * @param {string} goalData.title - Goal title
     * @param {number} goalData.target_amount - Target amount
     * @param {string} goalData.description - Optional description
     * @param {string} goalData.deadline - Optional deadline (YYYY-MM-DD)
     * @param {string} goalData.category - Optional category
     * @returns {Promise<Object>} Created goal
     */
    async createGoal(goalData) {
        try {
            const response = await api.post('/goals/', goalData);
            return response.data;
        } catch (error) {
            console.error('Error creating goal:', error);
            throw error;
        }
    }

    /**
     * Get a specific goal by ID
     * @param {number} goalId - Goal ID
     * @returns {Promise<Object>} Goal data
     */
    async getGoal(goalId) {
        try {
            const response = await api.get(`/goals/${goalId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching goal:', error);
            throw error;
        }
    }

    /**
     * Update a goal
     * @param {number} goalId - Goal ID
     * @param {Object} updates - Fields to update
     * @returns {Promise<Object>} Updated goal
     */
    async updateGoal(goalId, updates) {
        try {
            const response = await api.put(`/goals/${goalId}`, updates);
            return response.data;
        } catch (error) {
            console.error('Error updating goal:', error);
            throw error;
        }
    }

    /**
     * Delete a goal
     * @param {number} goalId - Goal ID
     * @returns {Promise<boolean>} Success status
     */
    async deleteGoal(goalId) {
        try {
            await api.delete(`/goals/${goalId}`);
            return true;
        } catch (error) {
            console.error('Error deleting goal:', error);
            throw error;
        }
    }

    /**
     * Update goal progress by adding amount
     * @param {number} goalId - Goal ID
     * @param {number} amount - Amount to add
     * @returns {Promise<Object>} Updated goal
     */
    async updateProgress(goalId, amount, type = 'manual') {
        try {
            const response = await api.put(`/goals/${goalId}/progress`, { amount, type });
            return response.data;
        } catch (error) {
            console.error('Error updating goal progress:', error);
            throw error;
        }
    }

    /**
     * Get goals summary statistics
     * @returns {Promise<Object>} Summary data
     */
    async getGoalsSummary() {
        try {
            const response = await api.get('/goals/summary');
            return response.data.data;
        } catch (error) {
            console.error('Error fetching goals summary:', error);
            throw error;
        }
    }

    /**
     * Get overdue goals
     * @returns {Promise<Array>} Array of overdue goals
     */
    async getOverdueGoals() {
        try {
            const response = await api.get('/goals/overdue');
            return response.data;
        } catch (error) {
            console.error('Error fetching overdue goals:', error);
            throw error;
        }
    }

    /**
     * Get goals near deadline
     * @param {number} days - Number of days to look ahead (default: 7)
     * @returns {Promise<Array>} Array of goals near deadline
     */
    async getGoalsNearDeadline(days = 7) {
        try {
            const response = await api.get(`/goals/near-deadline?days=${days}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching goals near deadline:', error);
            throw error;
        }
    }

    /**
     * Get goals by category
     * @param {string} category - Category to filter by
     * @returns {Promise<Array>} Array of goals in category
     */
    async getGoalsByCategory(category) {
        try {
            const response = await api.get(`/goals/category/${category}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching goals by category:', error);
            throw error;
        }
    }

    /**
     * Get available goal categories
     * @returns {Promise<Array>} Array of category objects
     */
    async getGoalCategories() {
        try {
            const response = await api.get('/goals/categories');
            return response.data.data;
        } catch (error) {
            console.error('Error fetching goal categories:', error);
            throw error;
        }
    }

    /**
     * Search goals with multiple filters
     * @param {string} searchTerm - Search term
     * @param {string} status - Status filter
     * @param {string} category - Category filter
     * @param {number} minAmount - Minimum amount filter
     * @param {number} maxAmount - Maximum amount filter
     * @returns {Promise<Array>} Array of goals
     */
    async searchGoals(searchTerm = null, status = null, category = null, minAmount = null, maxAmount = null) {
        try {
            const params = new URLSearchParams();
            if (searchTerm) params.append('search_term', searchTerm);
            if (status) params.append('status', status);
            if (category) params.append('category', category);
            if (minAmount) params.append('min_amount', minAmount);
            if (maxAmount) params.append('max_amount', maxAmount);
            
            const response = await api.get(`/goals/search?${params.toString()}`);
            return response.data;
        } catch (error) {
            console.error('Error searching goals:', error);
            throw error;
        }
    }

    /**
     * Get goal progress information
     * @param {number} goalId - Goal ID
     * @returns {Promise<Object>} Progress data
     */
    async getGoalProgress(goalId) {
        try {
            const response = await api.get(`/goals/${goalId}/progress-info`);
            return response.data.data;
        } catch (error) {
            console.error('Error fetching goal progress:', error);
            throw error;
        }
    }

    /**
     * Get detailed goals statistics
     * @returns {Promise<Object>} Statistics data
     */
    async getGoalsStatistics() {
        try {
            const response = await api.get('/goals/statistics');
            return response.data.data;
        } catch (error) {
            console.error('Error fetching goals statistics:', error);
            throw error;
        }
    }

    /**
     * Get active goals
     * @returns {Promise<Array>} Array of active goals
     */
    async getActiveGoals() {
        return this.getGoals('active');
    }

    /**
     * Get completed goals
     * @returns {Promise<Array>} Array of completed goals
     */
    async getCompletedGoals() {
        return this.getGoals('completed');
    }
}

const goalService = new GoalService();
export default goalService; 