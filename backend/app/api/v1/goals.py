from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.facade.goal_facade import GoalFacade
from app.utils.decorators.error_handler import handle_errors
from flask import request

# Namespace

goals_ns = Namespace('goals', description='Goals management')
goal_facade = GoalFacade()

# Modelos para Swagger y validación

goal_model = goals_ns.model("Goal", {
    "id": fields.Integer,
    "title": fields.String,
    "description": fields.String,
    "target_amount": fields.Float,
    "current_amount": fields.Float,
    "deadline": fields.String,
    "category": fields.String,
    "status": fields.String,
    "created_at": fields.String,
    "updated_at": fields.String,
    "progress_percentage": fields.Float,
    "days_remaining": fields.Integer,
    "linked_account_id": fields.Integer,
    "linked_amount": fields.Float,
    "linked_account": fields.Raw,
})

goal_create_model = goals_ns.model("GoalCreate", {
    "title": fields.String(required=True),
    "target_amount": fields.Float(required=True),
    "description": fields.String,
    "deadline": fields.String,
    "category": fields.String,
    "linked_account_id": fields.Integer,
    "linked_amount": fields.Float,
})

progress_update_model = goals_ns.model("ProgressUpdate", {
    "amount": fields.Float(required=True),
    "type": fields.String(default="manual"),
})

# Endpoints

@goals_ns.route('/')
class GoalsListResource(Resource):
    @jwt_required()
    @goals_ns.marshal_with(goal_model, as_list=True)
    @handle_errors
    def get(self):
        """Get all goals for the authenticated user"""
        user_id = get_jwt_identity()
        status = request.args.get('status')
        category = request.args.get('category')
        return goal_facade.get_user_goals(user_id, status, category)

    @jwt_required()
    @goals_ns.expect(goal_create_model, validate=True)
    @goals_ns.marshal_with(goal_model)
    @goals_ns.response(201, "Goal created successfully")
    @handle_errors
    def post(self):
        """Create a new goal for the authenticated user"""
        user_id = get_jwt_identity()
        data = goals_ns.payload
        return goal_facade.create_goal(user_id,**data), 201
            

@goals_ns.route('/<int:goal_id>')
class GoalResource(Resource):
    @jwt_required()
    @goals_ns.marshal_with(goal_model)
    @goals_ns.response(404, "Goal not found")
    @handle_errors
    def get(self, goal_id):
        """Get a specific goal by ID"""
        user_id = get_jwt_identity()
        return goal_facade.get_goal_by_id(goal_id, user_id)

    @jwt_required()
    @goals_ns.expect(goal_create_model, validate=True)
    @goals_ns.marshal_with(goal_model)
    @handle_errors
    def put(self, goal_id):
        """Update a specific goal"""
        user_id = get_jwt_identity()
        data = goals_ns.payload
        return goal_facade.update_goal(goal_id, user_id, **data)

    @jwt_required()
    @goals_ns.response(204, "Goal deleted successfully")
    @handle_errors
    def delete(self, goal_id):
        """Delete a specific goal"""
        user_id = get_jwt_identity()
        goal_facade.delete_goal(goal_id, user_id)
        return '', 204

@goals_ns.route('/<int:goal_id>/progress')
class GoalProgressResource(Resource):
    @jwt_required()
    @goals_ns.expect(progress_update_model, validate=True)
    @goals_ns.marshal_with(goal_model)
    @handle_errors
    def put(self, goal_id):
        """Update goal progress by adding amount"""
        user_id = get_jwt_identity()
        data = goals_ns.payload
        progress_type = data.get('type', 'manual')
        return goal_facade.update_goal_progress(goal_id, user_id, data['amount'], progress_type)

@goals_ns.route('/summary')
class GoalsSummaryResource(Resource):
    @jwt_required()
    @handle_errors
    def get(self):
        """Get summary statistics for user goals"""
        user_id = get_jwt_identity()
        summary = goal_facade.get_goals_summary(user_id)
        return {
            'success': True,
            'data': summary,
            'message': 'Goals summary retrieved successfully'
        }, 200

@goals_ns.route('/overdue')
class OverdueGoalsResource(Resource):
    @jwt_required()
    @goals_ns.marshal_with(goal_model, as_list=True)
    @handle_errors
    def get(self):
        """Get all overdue goals for the user"""
        user_id = get_jwt_identity()
        return goal_facade.get_overdue_goals(user_id)

@goals_ns.route('/near-deadline')
class NearDeadlineGoalsResource(Resource):
    @jwt_required()
    @goals_ns.marshal_with(goal_model, as_list=True)
    @handle_errors
    def get(self):
        """Get goals with deadline within specified days"""
        user_id = get_jwt_identity()
        days = request.args.get('days', 7, type=int)
        return goal_facade.get_goals_near_deadline(user_id, days)

@goals_ns.route('/category/<category>')
class GoalsByCategoryResource(Resource):
    @jwt_required()
    @goals_ns.marshal_with(goal_model, as_list=True)
    @handle_errors
    def get(self, category):
        """Get goals filtered by category"""
        user_id = get_jwt_identity()
        return goal_facade.get_goals_by_category(user_id, category)

@goals_ns.route('/categories')
class GoalCategoriesResource(Resource):
    @jwt_required()
    @handle_errors
    def get(self):
        """Get available goal categories"""
        categories = goal_facade.get_goal_categories()
        return {
            'success': True,
            'data': categories,
            'message': 'Goal categories retrieved successfully'
        }, 200

@goals_ns.route('/search')
class GoalsSearchResource(Resource):
    @jwt_required()
    @goals_ns.marshal_with(goal_model, as_list=True)
    @handle_errors
    def get(self):
        """Search goals with multiple filters"""
        user_id = get_jwt_identity()
        search_term = request.args.get('search_term')
        status = request.args.get('status')
        category = request.args.get('category')
        min_amount = request.args.get('min_amount', type=float)
        max_amount = request.args.get('max_amount', type=float)
        
        return goal_facade.search_goals(
            user_id, search_term, status, category, min_amount, max_amount
        )

@goals_ns.route('/statistics')
class GoalsStatisticsResource(Resource):
    @jwt_required()
    @handle_errors
    def get(self):
        """Get detailed statistics for user goals"""
        user_id = get_jwt_identity()
        statistics = goal_facade.get_goals_statistics(user_id)
        return {
            'success': True,
            'data': statistics,
            'message': 'Goals statistics retrieved successfully'
        }, 200

@goals_ns.route('/<int:goal_id>/progress-info')
class GoalProgressInfoResource(Resource):
    @jwt_required()
    @handle_errors
    def get(self, goal_id):
        """Get goal progress information"""
        user_id = get_jwt_identity()
        progress = goal_facade.get_goal_progress(goal_id, user_id)
        return {
            'success': True,
            'data': progress,
            'message': 'Goal progress retrieved successfully'
        }, 200 