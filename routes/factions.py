from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Faction, User, db
import random
import string

bp = Blueprint('factions', __name__)

def generate_invitation_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@bp.route('/faction/create', methods=['POST'])
@login_required
def create_faction():
    data = request.get_json()
    faction_name = data.get('name')
    if Faction.query.filter_by(name=faction_name).first():
        return jsonify({'error': 'Faction name already exists'}), 400
    
    invitation_code = generate_invitation_code()
    new_faction = Faction(name=faction_name, invitation_code=invitation_code, leader_id=current_user.id)
    current_user.faction = new_faction
    db.session.add(new_faction)
    db.session.commit()
    return jsonify({'message': 'Faction created successfully', 'invitation_code': invitation_code}), 201

@bp.route('/faction/join', methods=['POST'])
@login_required
def join_faction():
    data = request.get_json()
    invitation_code = data.get('invitation_code')
    faction = Faction.query.filter_by(invitation_code=invitation_code).first()
    if not faction:
        return jsonify({'error': 'Invalid invitation code'}), 400
    current_user.faction = faction
    db.session.commit()
    return jsonify({'message': 'Joined faction successfully'}), 200

@bp.route('/faction/members', methods=['GET'])
@login_required
def get_faction_members():
    if not current_user.faction:
        return jsonify({'error': 'You are not in a faction'}), 400
    members = User.query.filter_by(faction_id=current_user.faction.id).all()
    return jsonify({'members': [member.username for member in members]}), 200
