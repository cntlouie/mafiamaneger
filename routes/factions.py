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

# Keep the existing code below this point
