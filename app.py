import os
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, current_user, login_required

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

database_url = os.environ.get("DATABASE_URL")
if database_url:
    print("DATABASE_URL is set")
else:
    print("DATABASE_URL is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['SECRET_KEY'] = os.urandom(24)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    print(f"Received request for index page from {request.remote_addr}")
    return render_template('index.html')

@app.route('/register')
def register():
    print(f"Received request for register page from {request.remote_addr}")
    return render_template('register.html')

@app.route('/login')
def login():
    print(f"Received request for login page from {request.remote_addr}")
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    print(f"Received request for dashboard page from {request.remote_addr}")
    return render_template('dashboard.html')

# Import and register blueprints after all route definitions
from routes import auth, stats, factions
app.register_blueprint(auth.bp)
app.register_blueprint(stats.bp)
app.register_blueprint(factions.bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
