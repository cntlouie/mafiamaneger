from flask import Blueprint, render_template, request, jsonify, abort, current_app
from flask_login import login_required, current_user
from models import User, db, FeatureAccess
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime, timedelta

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
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    logger.info(f"Admin dashboard accessed by user {current_user.id}")
    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_admins=total_admins,
                           new_users_last_week=new_users_last_week,
                           users_with_advanced_stats=users_with_advanced_stats,
                           users_with_faction_management=users_with_faction_management,
                           users_with_leaderboard=users_with_leaderboard,
                           recent_users=recent_users)

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