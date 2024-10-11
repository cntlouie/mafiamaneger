from flask import Blueprint, render_template, request, jsonify, abort, current_app, redirect, url_for
from flask_login import login_required, current_user
from models import User, FeatureAccess, db
from functools import wraps
import logging

bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_admins = User.query.filter_by(is_admin=True).count()
    new_users_last_week = User.query.filter(User.created_at >= (db.func.now() - db.text("interval '7 days'"))).count()
    users_with_advanced_stats = FeatureAccess.query.filter_by(feature='advanced_stats', enabled=True).count()
    users_with_faction_management = FeatureAccess.query.filter_by(feature='faction_management', enabled=True).count()
    users_with_leaderboard = FeatureAccess.query.filter_by(feature='leaderboard', enabled=True).count()
    users_with_faction_creation = FeatureAccess.query.filter_by(feature='faction_creation', enabled=True).count()

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_admins=total_admins,
                           new_users_last_week=new_users_last_week,
                           users_with_advanced_stats=users_with_advanced_stats,
                           users_with_faction_management=users_with_faction_management,
                           users_with_leaderboard=users_with_leaderboard,
                           users_with_faction_creation=users_with_faction_creation)

@bp.route('/admin/users')
@login_required
@admin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    
    query = User.query
    if search_query:
        query = query.filter(User.username.ilike(f'%{search_query}%'))
    
    users = query.paginate(page=page, per_page=10, error_out=False)
    total_users = User.query.count()
    total_admins = User.query.filter_by(is_admin=True).count()
    
    return render_template('admin/users.html', users=users, search_query=search_query, total_users=total_users, total_admins=total_admins)

@bp.route('/admin/feature_access', methods=['GET'])
@login_required
@admin_required
def manage_feature_access():
    users = User.query.all()
    features = ['faction_creation', 'advanced_stats', 'leaderboard', 'faction_management']
    return render_template('admin/feature_access.html', users=users, features=features)

@bp.route('/admin/feature_access/update', methods=['POST'])
@login_required
@admin_required
def update_feature_access():
    try:
        feature_access_data = request.json
        logger.info(f"Received feature access update request from admin {current_user.id}")
        logger.debug(f"Feature access data: {feature_access_data}")

        if not feature_access_data:
            logger.warning("No feature access data received")
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        for user_id, features in feature_access_data.items():
            user = User.query.get(int(user_id))
            if not user:
                logger.warning(f"User with ID {user_id} not found during feature access update")
                continue

            logger.info(f"Updating feature access for user {user.id} ({user.username})")
            for feature, enabled in features.items():
                if feature == 'faction_creation' and not current_user.is_admin:
                    logger.warning(f"Non-admin user {current_user.id} attempted to grant faction creation permission")
                    continue

                feature_access = FeatureAccess.query.filter_by(user_id=user.id, feature=feature).first()
                if feature_access:
                    if enabled:
                        logger.info(f"Updating existing feature access: {feature} -> enabled")
                        feature_access.enabled = True
                    else:
                        logger.info(f"Revoking feature access: {feature}")
                        db.session.delete(feature_access)
                elif enabled:
                    logger.info(f"Creating new feature access: {feature} -> enabled")
                    new_feature_access = FeatureAccess(user_id=user.id, feature=feature, enabled=True)
                    db.session.add(new_feature_access)

        db.session.commit()
        logger.info(f"Feature access bulk update completed successfully by admin {current_user.id}")
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating feature access: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/admin/users/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        return jsonify({'error': 'You cannot change your own admin status'}), 400
    
    user.is_admin = not user.is_admin
    db.session.commit()
    return jsonify({'success': True, 'is_admin': user.is_admin})

@bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        return jsonify({'error': 'You cannot delete your own account'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/admin/bulk_action', methods=['POST'])
@login_required
@admin_required
def bulk_action():
    action = request.form.get('action')
    user_ids = request.form.getlist('user_ids[]')
    
    if not action or not user_ids:
        return jsonify({'error': 'Invalid request'}), 400
    
    if action == 'delete':
        User.query.filter(User.id.in_(user_ids), User.id != current_user.id).delete(synchronize_session=False)
    elif action == 'toggle_admin':
        users = User.query.filter(User.id.in_(user_ids), User.id != current_user.id)
        for user in users:
            user.is_admin = not user.is_admin
    
    db.session.commit()
    return redirect(url_for('admin.list_users'))

@bp.route('/admin/logs')
@login_required
@admin_required
def view_logs():
    return render_template('admin/logs.html')

@bp.route('/admin/fetch_logs')
@login_required
@admin_required
def fetch_logs():
    log_level = request.args.get('level', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Implement log fetching logic here
    # This is a placeholder, you'll need to implement the actual log fetching
    logs = ["Log entry 1", "Log entry 2", "Log entry 3"]
    
    return jsonify({'logs': logs})
