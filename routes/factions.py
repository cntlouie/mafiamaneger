from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import User, Faction, FeatureAccess, db
import secrets

bp = Blueprint('factions', __name__)

@bp.route('/faction/create', methods=['POST'])
@login_required
def create_faction():
    # Check if the user has permission to create a faction
    feature_access = FeatureAccess.query.filter_by(user_id=current_user.id, feature='faction_creation').first()
    if not feature_access or not feature_access.enabled:
        return jsonify({'error': 'You do not have permission to create a faction'}), 403

    data = request.get_json()
    faction_name = data.get('name')

    if not faction_name:
        return jsonify({'error': 'Faction name is required'}), 400

    existing_faction = Faction.query.filter_by(name=faction_name).first()
    if existing_faction:
        return jsonify({'error': 'Faction name already exists'}), 400

    if current_user.faction:
        return jsonify({'error': 'You are already in a faction'}), 400

    invitation_code = secrets.token_urlsafe(8)
    new_faction = Faction(name=faction_name, invitation_code=invitation_code, leader_username=current_user.username)
    current_user.faction = new_faction

    db.session.add(new_faction)
    db.session.commit()

    return jsonify({
        'message': 'Faction created successfully',
        'faction_id': new_faction.id,
        'invitation_code': invitation_code
    }), 201

@bp.route('/faction/join', methods=['POST'])
@login_required
def join_faction():
    data = request.get_json()
    invitation_code = data.get('invitation_code')

    if not invitation_code:
        return jsonify({'error': 'Invitation code is required'}), 400

    faction = Faction.query.filter_by(invitation_code=invitation_code).first()
    if not faction:
        return jsonify({'error': 'Invalid invitation code'}), 400

    if current_user.faction:
        return jsonify({'error': 'You are already in a faction'}), 400

    current_user.faction = faction
    db.session.commit()

    return jsonify({'message': 'Successfully joined the faction'}), 200

@bp.route('/faction/members', methods=['GET'])
@login_required
def get_faction_members():
    if not current_user.faction:
        return jsonify({'error': 'You are not in a faction'}), 400

    members = User.query.filter_by(faction_id=current_user.faction.id).all()
    member_list = [{'id': member.id, 'username': member.username} for member in members]

    return jsonify({'members': member_list}), 200

@bp.route('/faction/leave', methods=['POST'])
@login_required
def leave_faction():
    if not current_user.faction:
        return jsonify({'error': 'You are not in a faction'}), 400

    if current_user.faction.leader_username == current_user.username:
        return jsonify({'error': 'Faction leader cannot leave the faction'}), 400

    current_user.faction = None
    db.session.commit()

    return jsonify({'message': 'Successfully left the faction'}), 200

@bp.route('/faction/details', methods=['GET'])
@login_required
def get_faction_details():
    if not current_user.faction:
        return jsonify({'error': 'You are not in a faction'}), 400

    faction = current_user.faction
    leader = User.query.filter_by(username=faction.leader_username).first()

    return jsonify({
        'id': faction.id,
        'name': faction.name,
        'leader': {'id': leader.id, 'username': leader.username},
        'member_count': len(faction.members),
        'invitation_code': faction.invitation_code if faction.leader_username == current_user.username else None
    }), 200
