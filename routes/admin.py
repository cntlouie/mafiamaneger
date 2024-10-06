from flask import Blueprint, render_template, request, jsonify, abort, current_app
from flask_login import login_required, current_user
from models import User, db, FeatureAccess, Faction
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime, timedelta
import uuid

bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            logger.warning(f"Unauthenticated access attempt to admin area")
            return current_app.login_manager.unauthorized()
        if not current_user.is_admin:
            logger.warning(f"Non-admin access attempt to admin area by user {current_user.id}")
            abort(403)
        logger.info(f"Admin access granted to user {current_user.id}")
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_admins = User.query.filter_by(is_admin=True).count()
    
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_last_week = User.query.filter(User.created_at >= one_week_ago).count()
    
    users_with_advanced_stats = FeatureAccess.query.filter_by(feature='advanced_stats', enabled=True).count()
    users_with_faction_management = FeatureAccess.query.filter_by(feature='faction_management', enabled=True).count()
    users_with_leaderboard = FeatureAccess.query.filter_by(feature='leaderboard', enabled=True).count()
    
    logger.info(f"Admin dashboard accessed by user {current_user.id}")
    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_admins=total_admins,
                           new_users_last_week=new_users_last_week,
                           users_with_advanced_stats=users_with_advanced_stats,
                           users_with_faction_management=users_with_faction_management,
                           users_with_leaderboard=users_with_leaderboard)

@bp.route('/admin/users')
@login_required
@admin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_query = request.args.get('search', '')
    
    users_query = User.query
    if search_query:
        users_query = users_query.filter(User.username.ilike(f'%{search_query}%') | User.email.ilike(f'%{search_query}%'))
    
    users = users_query.order_by(User.id).paginate(page=page, per_page=per_page, error_out=False)
    
    total_users = users_query.count()
    total_admins = users_query.filter_by(is_admin=True).count()
    
    logger.info(f"User list accessed by admin {current_user.id}")
    return render_template('admin/users.html', users=users, search_query=search_query, total_users=total_users, total_admins=total_admins)

@bp.route('/admin/users/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        logger.warning(f"Admin {current_user.id} attempted to change their own admin status")
        return jsonify({'error': 'You cannot change your own admin status'}), 400
    user.is_admin = not user.is_admin
    db.session.commit()
    logger.info(f"Admin status toggled for user {user_id} by admin {current_user.id}")
    return jsonify({'success': True, 'is_admin': user.is_admin})

@bp.route('/admin/feature_access')
@login_required
@admin_required
def manage_feature_access():
    users = User.query.all()
    features = ['advanced_stats', 'faction_management', 'leaderboard']
    logger.info(f"Feature access management accessed by admin {current_user.id}")
    return render_template('admin/feature_access.html', users=users, features=features)

@bp.route('/admin/feature_access/update', methods=['POST'])
@login_required
@admin_required
def update_feature_access():
    user_id = request.form.get('user_id')
    feature = request.form.get('feature')
    enabled = request.form.get('enabled') == 'true'

    user = User.query.get_or_404(user_id)
    feature_access = FeatureAccess.query.filter_by(user_id=user.id, feature=feature).first()

    if feature_access:
        feature_access.enabled = enabled
    else:
        feature_access = FeatureAccess(user_id=user.id, feature=feature, enabled=enabled)
        db.session.add(feature_access)

    try:
        db.session.commit()
        logger.info(f"Feature access updated for user {user_id} by admin {current_user.id}")
        return jsonify({'success': True})
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error while updating feature access for user {user_id}: {str(e)}")
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@bp.route('/admin/faction_management')
@login_required
@admin_required
def faction_management():
    logger.info(f"Faction management accessed by admin {current_user.id}")
    return render_template('admin/faction_management.html')

@bp.route('/admin/faction/create', methods=['POST'])
@login_required
@admin_required
def create_faction():
    data = request.get_json()
    name = data.get('name')
    leader_username = data.get('leader_username')

    if not name or not leader_username:
        return jsonify({'error': 'Faction name and leader username are required'}), 400

    leader = User.query.filter_by(username=leader_username).first()
    if not leader:
        return jsonify({'error': 'Leader not found'}), 404

    try:
        new_faction = Faction(name=name, leader_username=leader_username, invitation_code=str(uuid.uuid4())[:8])
        db.session.add(new_faction)
        leader.faction = new_faction
        db.session.commit()
        logger.info(f"Faction '{name}' created by admin {current_user.id}")
        return jsonify({'success': True, 'message': 'Faction created successfully'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error while creating faction: {str(e)}")
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@bp.route('/admin/factions')
@login_required
@admin_required
def get_factions():
    factions = Faction.query.all()
    factions_data = [{
        'id': faction.id,
        'name': faction.name,
        'leader_username': faction.leader_username,
        'member_count': len(faction.members)
    } for faction in factions]
    return jsonify({'factions': factions_data})

@bp.route('/admin/faction/<int:faction_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_faction(faction_id):
    faction = Faction.query.get_or_404(faction_id)
    try:
        for member in faction.members:
            member.faction = None
        db.session.delete(faction)
        db.session.commit()
        logger.info(f"Faction {faction_id} deleted by admin {current_user.id}")
        return jsonify({'success': True, 'message': 'Faction deleted successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error while deleting faction {faction_id}: {str(e)}")
        return jsonify({'error': 'Database error', 'message': str(e)}), 500
