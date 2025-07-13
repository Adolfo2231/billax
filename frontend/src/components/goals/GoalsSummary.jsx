import React from 'react';

const GoalsSummary = ({ summary }) => (
  <div className="goals-summary">
    <div className="summary-card">
      <h3>Total Goals</h3>
      <p>{summary.total_goals || 0}</p>
    </div>
    <div className="summary-card">
      <h3>Active Goals</h3>
      <p>{summary.active_goals || 0}</p>
    </div>
    <div className="summary-card">
      <h3>Completed</h3>
      <p>{summary.completed_goals || 0}</p>
    </div>
    <div className="summary-card">
      <h3>Progress</h3>
      <p>{summary.overall_progress?.toFixed(1) || 0}%</p>
    </div>
  </div>
);

export default GoalsSummary; 