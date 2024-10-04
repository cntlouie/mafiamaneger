from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Stats, db
from sqlalchemy.exc import SQLAlchemyError, DataError

bp = Blueprint('stats', __name__)

@bp.route('/stats', methods=['POST'])
@login_required
def update_stats():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate and convert data to integers
        for key, value in data.items():
            try:
                data[key] = int(value)
                if data[key] < 0:
                    return jsonify({'error': f'Invalid value for {key}. Must be a non-negative integer.'}), 400
            except ValueError:
                return jsonify({'error': f'Invalid value for {key}. Must be a valid integer.'}), 400

        new_stats = Stats(user_id=current_user.id, **data)
        db.session.add(new_stats)
        db.session.commit()
        return jsonify({'message': 'Stats updated successfully'}), 200
    except DataError as e:
        db.session.rollback()
        return jsonify({'error': 'Data error. One or more values exceed the maximum allowed value.', 'details': str(e)}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500

@bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    try:
        current_stats = Stats.query.filter_by(user_id=current_user.id).order_by(Stats.timestamp.desc()).first()
        previous_stats = Stats.query.filter_by(user_id=current_user.id).order_by(Stats.timestamp.desc()).offset(1).first()

        if current_stats:
            total_battles = current_stats.total_wins + current_stats.total_losses
            win_rate = (current_stats.total_wins / total_battles * 100) if total_battles > 0 else 0
            previous_total_battles = previous_stats.total_wins + previous_stats.total_losses if previous_stats else total_battles
            previous_win_rate = (previous_stats.total_wins / previous_total_battles * 100) if previous_total_battles > 0 else win_rate

            stats_data = {
                'total_wins': {'current': current_stats.total_wins, 'previous': previous_stats.total_wins if previous_stats else current_stats.total_wins},
                'total_losses': {'current': current_stats.total_losses, 'previous': previous_stats.total_losses if previous_stats else current_stats.total_losses},
                'assaults_won': {'current': current_stats.assaults_won, 'previous': previous_stats.assaults_won if previous_stats else current_stats.assaults_won},
                'assaults_lost': {'current': current_stats.assaults_lost, 'previous': previous_stats.assaults_lost if previous_stats else current_stats.assaults_lost},
                'defending_battles_won': {'current': current_stats.defending_battles_won, 'previous': previous_stats.defending_battles_won if previous_stats else current_stats.defending_battles_won},
                'defending_battles_lost': {'current': current_stats.defending_battles_lost, 'previous': previous_stats.defending_battles_lost if previous_stats else current_stats.defending_battles_lost},
                'win_rate': {'current': round(win_rate, 2), 'previous': round(previous_win_rate, 2)},
                'kills': {'current': current_stats.kills, 'previous': previous_stats.kills if previous_stats else current_stats.kills},
                'destroyed_traps': {'current': current_stats.destroyed_traps, 'previous': previous_stats.destroyed_traps if previous_stats else current_stats.destroyed_traps},
                'lost_associates': {'current': current_stats.lost_associates, 'previous': previous_stats.lost_associates if previous_stats else current_stats.lost_associates},
                'lost_traps': {'current': current_stats.lost_traps, 'previous': previous_stats.lost_traps if previous_stats else current_stats.lost_traps},
                'healed_associates': {'current': current_stats.healed_associates, 'previous': previous_stats.healed_associates if previous_stats else current_stats.healed_associates},
                'wounded_enemy_associates': {'current': current_stats.wounded_enemy_associates, 'previous': previous_stats.wounded_enemy_associates if previous_stats else current_stats.wounded_enemy_associates},
                'enemy_turfs_destroyed': {'current': current_stats.enemy_turfs_destroyed, 'previous': previous_stats.enemy_turfs_destroyed if previous_stats else current_stats.enemy_turfs_destroyed},
                'turf_destroyed_times': {'current': current_stats.turf_destroyed_times, 'previous': previous_stats.turf_destroyed_times if previous_stats else current_stats.turf_destroyed_times},
                'eliminated_enemy_influence': {'current': current_stats.eliminated_enemy_influence, 'previous': previous_stats.eliminated_enemy_influence if previous_stats else current_stats.eliminated_enemy_influence},
            }
            return jsonify(stats_data), 200
        return jsonify({'error': 'No stats found'}), 404
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500
