from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Stats, db

bp = Blueprint('stats', __name__)

@bp.route('/stats', methods=['POST'])
@login_required
def update_stats():
    data = request.get_json()
    new_stats = Stats(user_id=current_user.id, **data)
    db.session.add(new_stats)
    db.session.commit()
    return jsonify({'message': 'Stats updated successfully'}), 200

@bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    stats = Stats.query.filter_by(user_id=current_user.id).order_by(Stats.timestamp.desc()).first()
    if stats:
        return jsonify({
            'total_wins': stats.total_wins,
            'total_losses': stats.total_losses,
            'assaults_won': stats.assaults_won,
            'assaults_lost': stats.assaults_lost,
            'defending_battles_won': stats.defending_battles_won,
            'defending_battles_lost': stats.defending_battles_lost,
            'kills': stats.kills,
            'destroyed_traps': stats.destroyed_traps,
            'lost_associates': stats.lost_associates,
            'lost_traps': stats.lost_traps,
            'healed_associates': stats.healed_associates,
            'wounded_enemy_associates': stats.wounded_enemy_associates,
            'enemy_turfs_destroyed': stats.enemy_turfs_destroyed,
            'turf_destroyed_times': stats.turf_destroyed_times,
            'eliminated_enemy_influence': stats.eliminated_enemy_influence
        }), 200
    return jsonify({'error': 'No stats found'}), 404
