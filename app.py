import os
import logging
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, current_user, login_required
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Import models after db is initialized
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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Import and register blueprints after all route definitions
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

def setup_database():
    with app.app_context():
        db.create_all()
        ensure_admin_exists()
        logger.info("Database tables created and admin user ensured")

if __name__ == "__main__":
    setup_database()
    app.run(host="0.0.0.0", port=5000)