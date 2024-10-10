from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from models import User
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)
csrf = CSRFProtect()

@bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    db = SQLAlchemy()
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"New user registered: {username}")
        return jsonify({'message': 'User registered successfully'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({'error': 'An error occurred while registering the user'}), 500

@bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        db = SQLAlchemy()
        user = User.query.filter_by(username=username).first()
        logger.info(f"Login attempt for user: {username}")

        if user and user.check_password(password):
            login_user(user)
            logger.info(f"User {user.username} logged in successfully. Admin status: {user.is_admin}")
            return jsonify({
                'message': 'Logged in successfully',
                'redirect': url_for('admin.admin_dashboard') if user.is_admin else url_for('dashboard'),
                'is_admin': user.is_admin
            }), 200
        else:
            logger.warning(f"Failed login attempt for user: {username}")
            return jsonify({'error': 'Invalid username or password'}), 401
    except SQLAlchemyError as e:
        logger.error(f"Database error during login: {str(e)}")
        return jsonify({'error': 'A database error occurred'}), 500
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

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

def init_auth(app):
    limiter.init_app(app)
    csrf.init_app(app)
