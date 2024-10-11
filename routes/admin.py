@bp.route('/admin/feature_access/update', methods=['POST'])
@login_required
@admin_required
def update_feature_access():
    try:
        feature_access_data = request.json
        logger.info(f"Received feature access update request from admin {current_user.id}")
        logger.debug(f"Feature access data: {feature_access_data}")

        if not feature_access_data:
            logger.warning("No feature access data received")
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        for user_id, features in feature_access_data.items():
            user = User.query.get(int(user_id))
            if not user:
                logger.warning(f"User with ID {user_id} not found during feature access update")
                continue

            logger.info(f"Updating feature access for user {user.id} ({user.username})")
            for feature, enabled in features.items():
                if feature == 'faction_creation' and not current_user.is_admin:
                    logger.warning(f"Non-admin user {current_user.id} attempted to grant faction creation permission")
                    continue

                feature_access = FeatureAccess.query.filter_by(user_id=user.id, feature=feature).first()
                if feature_access:
                    logger.info(f"Updating existing feature access: {feature} -> {enabled}")
                    feature_access.enabled = enabled
                else:
                    logger.info(f"Creating new feature access: {feature} -> {enabled}")
                    new_feature_access = FeatureAccess(user_id=user.id, feature=feature, enabled=enabled)
                    db.session.add(new_feature_access)

        db.session.commit()
        logger.info(f"Feature access bulk update completed successfully by admin {current_user.id}")
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating feature access: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
