import os
import logging
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, current_user, login_required
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException
import json

class Base(DeclarativeBase):
    pass

def create_app():
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = app.logger

    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        logger.info("DATABASE_URL is set")
    else:
        logger.warning("DATABASE_URL is not set")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config['SECRET_KEY'] = os.urandom(24)

    # Create db instance inside create_app function
    db = SQLAlchemy(model_class=Base)
    db.init_app(app)

    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from models import User, Faction, Stats, FeatureAccess

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def index():
        logger.info(f"Received request for index page from {request.remote_addr}")
        return render_template('index.html')

    @app.route('/register')
    def register():
        logger.info(f"Received request for register page from {request.remote_addr}")
        return render_template('register.html')

    @app.route('/login')
    def login():
        logger.info(f"Received request for login page from {request.remote_addr}")
        return render_template('login.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        logger.info(f"Received request for dashboard page from {request.remote_addr}")
        return render_template('dashboard.html')

    @app.route('/health')
    def health_check():
        try:
            # Check database connection
            db.session.execute('SELECT 1')
            return jsonify({'status': 'healthy', 'database': 'connected'}), 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({'status': 'unhealthy', 'database': 'disconnected', 'error': str(e)}), 500

    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        response = e.get_response()
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500

    # Import and register blueprints
    from routes import auth, stats, factions, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(stats.bp)
    app.register_blueprint(factions.bp)
    app.register_blueprint(admin.bp)

    @app.route('/promote_first_user_to_admin')
    def promote_first_user_to_admin():
        try:
            first_user = User.query.first()
            if first_user:
                first_user.is_admin = True
                db.session.commit()
                logger.info(f'User {first_user.username} promoted to admin')
                return jsonify({'message': f'User {first_user.username} promoted to admin'}), 200
            else:
                logger.warning('No users found in the database')
                return jsonify({'message': 'No users found'}), 404
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Database error while promoting user to admin: {str(e)}')
            return jsonify({'error': 'Database error', 'message': str(e)}), 500
        except Exception as e:
            logger.error(f'Unexpected error while promoting user to admin: {str(e)}')
            return jsonify({'error': 'Unexpected error', 'message': str(e)}), 500

    def ensure_admin_exists():
        try:
            admin_user = User.query.filter_by(is_admin=True).first()
            if not admin_user:
                first_user = User.query.first()
                if first_user:
                    first_user.is_admin = True
                    db.session.commit()
                    logger.info(f"Promoted user {first_user.username} to admin")
                else:
                    logger.warning("No users found in the database")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Database error while ensuring admin exists: {str(e)}')
        except Exception as e:
            logger.error(f'Unexpected error while ensuring admin exists: {str(e)}')

    with app.app_context():
        db.create_all()
        ensure_admin_exists()
        logger.info("Database tables created and admin user ensured")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
