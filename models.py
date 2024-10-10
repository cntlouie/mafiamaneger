from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    stats = db.relationship('Stats', backref='user', lazy=True)
    faction_id = db.Column(db.Integer, db.ForeignKey('faction.id', name='fk_user_faction'), nullable=True)
    faction = db.relationship('Faction', back_populates='members')
    feature_access = db.relationship('FeatureAccess', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Stats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_wins = db.Column(db.Integer, default=0)
    total_losses = db.Column(db.Integer, default=0)
    assaults_won = db.Column(db.Integer, default=0)
    assaults_lost = db.Column(db.Integer, default=0)
    defending_battles_won = db.Column(db.Integer, default=0)
    defending_battles_lost = db.Column(db.Integer, default=0)
    kills = db.Column(db.BigInteger, default=0)
    destroyed_traps = db.Column(db.BigInteger, default=0)
    lost_associates = db.Column(db.BigInteger, default=0)
    lost_traps = db.Column(db.BigInteger, default=0)
    healed_associates = db.Column(db.BigInteger, default=0)
    wounded_enemy_associates = db.Column(db.BigInteger, default=0)
    enemy_turfs_destroyed = db.Column(db.Integer, default=0)
    turf_destroyed_times = db.Column(db.Integer, default=0)
    eliminated_enemy_influence = db.Column(db.BigInteger, default=0)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class Faction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    invitation_code = db.Column(db.String(16), unique=True, nullable=False)
    leader_username = db.Column(db.String(64), nullable=False)
    members = db.relationship('User', back_populates='faction', lazy=True)

class FeatureAccess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    feature = db.Column(db.String(64), nullable=False)
    enabled = db.Column(db.Boolean, default=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'feature', name='_user_feature_uc'),)
