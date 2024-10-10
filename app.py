from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException
from extensions import db
from flask_login import LoginManager, current_user
import os
import logging
from logging.handlers import RotatingFileHandler
import json

def create_app():
    app = Flask(__name__)

    # Configure logging
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_file = os.path.join(app.root_path, 'app.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=10)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        app.logger.info("DATABASE_URL is set")
    else:
        app.logger.warning("DATABASE_URL is not set")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config['SECRET_KEY'] = os.urandom(24)

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    # Import models after db initialization
    from models import User, Faction, Stats, FeatureAccess

    # Register blueprints
    from routes import auth, stats, factions, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(stats.bp)
    app.register_blueprint(factions.bp)
    app.register_blueprint(admin.bp)

    # Routes
    @app.route('/')
    def index():
        app.logger.info(f"Received request for index page from {request.remote_addr}")
        return render_template('index.html')

    @app.route('/register')
    def register():
        app.logger.info(f"Received request for register page from {request.remote_addr}")
        return render_template('register.html')

    @app.route('/login')
    def login():
        app.logger.info(f"Received request for login page from {request.remote_addr}")
        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        app.logger.info(f"Received request for dashboard page from {request.remote_addr}")
        return render_template('dashboard.html')

    @app.route('/health')
    def health_check():
        try:
            # Check database connection
            db.session.execute('SELECT 1')
            return jsonify({'status': 'healthy', 'database': 'connected'}), 200
        except Exception as e:
            app.logger.error(f"Health check failed: {str(e)}")
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
        app.logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500

    @app.route('/promote_first_user_to_admin')
    def promote_first_user_to_admin():
        try:
            first_user = User.query.first()
            if first_user:
                first_user.is_admin = True
                db.session.commit()
                app.logger.info(f'User {first_user.username} promoted to admin')
                return jsonify({'message': f'User {first_user.username} promoted to admin'}), 200
            else:
                app.logger.warning('No users found in the database')
                return jsonify({'message': 'No users found'}), 404
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f'Database error while promoting user to admin: {str(e)}')
            return jsonify({'error': 'Database error', 'message': str(e)}), 500
        except Exception as e:
            app.logger.error(f'Unexpected error while promoting user to admin: {str(e)}')
            return jsonify({'error': 'Unexpected error', 'message': str(e)}), 500

    def ensure_admin_exists():
        try:
            admin_user = User.query.filter_by(is_admin=True).first()
            if not admin_user:
                first_user = User.query.first()
                if first_user:
                    first_user.is_admin = True
                    db.session.commit()
                    app.logger.info(f"Promoted user {first_user.username} to admin")
                else:
                    app.logger.warning("No users found in the database")
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f'Database error while ensuring admin exists: {str(e)}')
        except Exception as e:
            app.logger.error(f'Unexpected error while ensuring admin exists: {str(e)}')

    with app.app_context():
        db.create_all()
        ensure_admin_exists()
        app.logger.info("Database tables created and admin user ensured")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
