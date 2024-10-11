from flask import Blueprint, render_template, request, jsonify, abort, current_app
from flask_login import login_required, current_user
from models import User, db
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
    
    logger.info(f"Admin dashboard accessed by user {current_user.id}")
    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_admins=total_admins,
                           new_users_last_week=new_users_last_week,
                           users_with_advanced_stats=users_with_advanced_stats,
                           users_with_faction_management=users_with_faction_management,
                           users_with_leaderboard=users_with_leaderboard)

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

# Keep the existing code below this point
