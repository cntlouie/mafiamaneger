from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from models import User, db
import logging

bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    logger.info(f"New user registered: {username}")
    return jsonify({'message': 'User registered successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    logger.info(f"Login attempt for user: {data.get('username')}")
    if user and user.check_password(data.get('password')):
        login_user(user)
        logger.info(f"User {user.username} logged in successfully. Admin status: {user.is_admin}")
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return jsonify({'message': 'Logged in successfully', 'redirect': next_page, 'is_admin': user.is_admin}), 200
        elif user.is_admin:
            return jsonify({'message': 'Logged in successfully', 'redirect': url_for('admin.admin_dashboard'), 'is_admin': True}), 200
        else:
            return jsonify({'message': 'Logged in successfully', 'redirect': url_for('dashboard'), 'is_admin': False}), 200
    logger.warning(f"Failed login attempt for user: {data.get('username')}")
    return jsonify({'error': 'Invalid username or password'}), 401

@bp.route('/logout')
@login_required
def logout():
    logger.info(f"User {current_user.username} logged out")
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@bp.route('/check_admin')
@login_required
def check_admin():
    logger.info(f"Checking admin status for user {current_user.username}")
    return jsonify({'is_admin': current_user.is_admin}), 200
