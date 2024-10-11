from flask import Blueprint, render_template, request, jsonify, abort, current_app, redirect, url_for
from flask_login import login_required, current_user
from models import User, FeatureAccess, db
from functools import wraps
import logging
from datetime import datetime, timedelta
import os

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
    users_with_faction_creation = FeatureAccess.query.filter_by(feature='faction_creation', enabled=True).count()
    
    logger.info(f"Admin dashboard accessed by user {current_user.id}")
    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_admins=total_admins,
                           new_users_last_week=new_users_last_week,
                           users_with_advanced_stats=users_with_advanced_stats,
                           users_with_faction_management=users_with_faction_management,
                           users_with_leaderboard=users_with_leaderboard,
                           users_with_faction_creation=users_with_faction_creation)

@bp.route('/admin/logs')
@login_required
@admin_required
def view_logs():
    return render_template('admin/logs.html')

@bp.route('/admin/fetch_logs')
@login_required
@admin_required
def fetch_logs():
    try:
        log_level = request.args.get('level', 'all')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        log_file_path = os.path.join(current_app.root_path, 'app.log')
        
        if not os.path.exists(log_file_path):
            return jsonify({'logs': ['No log file found.']}), 404

        with open(log_file_path, 'r') as log_file:
            logs = log_file.readlines()

        filtered_logs = []
        for log in logs:
            log_parts = log.split(' ', 2)
            if len(log_parts) < 3:
                continue
            
            try:
                log_datetime = datetime.strptime(f"{log_parts[0]} {log_parts[1]}", '%Y-%m-%d %H:%M:%S,%f')
            except ValueError:
                continue
            
            if start_date and log_datetime < datetime.strptime(start_date, '%Y-%m-%d'):
                continue
            if end_date and log_datetime > datetime.strptime(end_date, '%Y-%m-%d'):
                continue
            
            if log_level != 'all':
                if log_level.upper() not in log_parts[2]:
                    continue
            
            filtered_logs.append(log.strip())

        logger.info(f"Logs fetched by admin {current_user.id}")
        return jsonify({'logs': filtered_logs}), 200
    except Exception as e:
        logger.error(f"Error fetching logs: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching logs', 'details': str(e)}), 500

@bp.route('/admin/feature_access', methods=['GET'])
@login_required
@admin_required
def manage_feature_access():
    users = User.query.all()
    features = ['faction_creation', 'advanced_stats', 'leaderboard']
    return render_template('admin/feature_access.html', users=users, features=features)

@bp.route('/admin/feature_access/update', methods=['POST'])
@login_required
@admin_required
def update_feature_access():
    user_id = request.form.get('user_id')
    feature = request.form.get('feature')
    enabled = request.form.get('enabled') == 'true'

    if not user_id or not feature:
        return jsonify({'error': 'Invalid request'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if feature == 'faction_creation' and not current_user.is_admin:
        logger.warning(f"Non-admin user {current_user.id} attempted to grant faction creation permission")
        return jsonify({'error': 'Only admins can grant faction creation permission'}), 403

    feature_access = FeatureAccess.query.filter_by(user_id=user.id, feature=feature).first()
    if feature_access:
        feature_access.enabled = enabled
    else:
        feature_access = FeatureAccess(user_id=user.id, feature=feature, enabled=enabled)
        db.session.add(feature_access)

    db.session.commit()
    logger.info(f"Feature access updated for user {user.id}: {feature} set to {enabled} by admin {current_user.id}")
    return jsonify({'success': True}), 200

@bp.route('/admin/users')
@login_required
@admin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    
    users_query = User.query
    if search_query:
        users_query = users_query.filter(User.username.ilike(f'%{search_query}%'))
    
    users = users_query.paginate(page=page, per_page=20, error_out=False)
    total_users = User.query.count()
    total_admins = User.query.filter_by(is_admin=True).count()
    
    return render_template('admin/users.html', users=users, search_query=search_query, total_users=total_users, total_admins=total_admins)

@bp.route('/admin/users/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        return jsonify({'error': 'You cannot change your own admin status'}), 400
    
    user.is_admin = not user.is_admin
    db.session.commit()
    logger.info(f"Admin status toggled for user {user.id} by admin {current_user.id}")
    return jsonify({'success': True, 'is_admin': user.is_admin}), 200

@bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        return jsonify({'error': 'You cannot delete your own account'}), 400
    
    db.session.delete(user)
    db.session.commit()
    logger.info(f"User {user.id} deleted by admin {current_user.id}")
    return jsonify({'success': True}), 200

@bp.route('/admin/users/bulk_action', methods=['POST'])
@login_required
@admin_required
def bulk_action():
    action = request.form.get('action')
    user_ids = request.form.getlist('user_ids[]')
    
    if not action or not user_ids:
        return jsonify({'error': 'Invalid request'}), 400
    
    users = User.query.filter(User.id.in_(user_ids)).all()
    
    if action == 'delete':
        for user in users:
            if user != current_user:
                db.session.delete(user)
        db.session.commit()
        logger.info(f"Bulk delete action performed by admin {current_user.id}")
    elif action == 'toggle_admin':
        for user in users:
            if user != current_user:
                user.is_admin = not user.is_admin
        db.session.commit()
        logger.info(f"Bulk toggle admin action performed by admin {current_user.id}")
    
    return jsonify({'success': True}), 200

@bp.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if username and email:
            user.username = username
            user.email = email
            if password:
                user.set_password(password)
            
            db.session.commit()
            logger.info(f"User {user.id} edited by admin {current_user.id}")
            return redirect(url_for('admin.list_users'))
        
    return render_template('admin/edit_user.html', user=user)