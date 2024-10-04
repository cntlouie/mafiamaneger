from flask import Blueprint, render_template, request, jsonify, abort, current_app
from flask_login import login_required, current_user
from models import User, db, FeatureAccess
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
import logging

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
    logger.info(f"Admin dashboard accessed by user {current_user.id}")
    return render_template('admin/dashboard.html')

@bp.route('/admin/users')
@login_required
@admin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    logger.info(f"User list accessed by admin {current_user.id}")
    return render_template('admin/users.html', users=users)

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

@bp.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        if request.form['password']:
            user.set_password(request.form['password'])
        try:
            db.session.commit()
            logger.info(f"User {user_id} updated by admin {current_user.id}")
            return jsonify({'success': True, 'message': 'User updated successfully'})
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error while updating user {user_id}: {str(e)}")
            return jsonify({'error': 'Database error', 'message': str(e)}), 500
    return render_template('admin/edit_user.html', user=user)

@bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        logger.warning(f"Admin {current_user.id} attempted to delete their own account")
        return jsonify({'error': 'You cannot delete your own account'}), 400
    db.session.delete(user)
    db.session.commit()
    logger.info(f"User {user_id} deleted by admin {current_user.id}")
    return jsonify({'success': True})

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