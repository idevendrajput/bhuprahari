import cv2
import numpy as np
import json  # Import json for storing change_log
from datetime import datetime
# No removed current_app import as config is passed directly

from extensions import db  # Import db from extensions
from entities.models import ImageTile, AlertSession, AlertDetail  # Import new models
from services.firebase_service import FirebaseService  # Import FirebaseService


class ImageComparisonService:
    @staticmethod
    # Accept app_config as an argument
    def compare_images(image1_path, image2_path, app_config):
        try:
            img1 = cv2.imread(image1_path)
            img2 = cv2.imread(image2_path)

            if img1 is None or img2 is None:
                raise ValueError("Failed to load one or both images. Check paths and file integrity.")

            # Use app_config for image size
            target_size = (int(app_config['Maps_IMAGE_SIZE'].split('x')[0]),
                           int(app_config['Maps_IMAGE_SIZE'].split('x')[1]))
            img1 = cv2.resize(img1, target_size)
            img2 = cv2.resize(img2, target_size)

            diff = cv2.absdiff(img1, img2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blurred, 30, 255, cv2.THRESH_BINARY)  # Adjust threshold if needed

            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            total_change_area = 0
            min_contour_area_threshold = 100  # Filter out very small noisy changes

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > min_contour_area_threshold:
                    total_change_area += area

            image_area = thresh.shape[0] * thresh.shape[1]
            change_percent = (total_change_area / image_area) * 100 if image_area > 0 else 0

            return {
                "changed": change_percent > 0.1,  # Threshold for considering a change
                "change_percent": round(change_percent, 2),
                "message": "Comparison successful."
            }
        except Exception as e:
            print(f"Error in image comparison: {e}")
            return {"changed": False, "change_percent": 0.0, "message": f"Comparison failed: {str(e)}", "error": True}

    @staticmethod
    # Accept app_config as an argument
    def run_comparison_for_area(area_config_id, app_config):
        print(f"Starting image comparison for AreaConfig ID: {area_config_id}")

        # --- Alert Session Management ---
        alert_session = AlertSession(
            area_config_id=area_config_id,
            status='IN_PROGRESS',
            start_time=datetime.utcnow()
        )
        db.session.add(alert_session)
        db.session.commit()  # Commit to get alert_session.id

        total_changes_in_session = 0
        session_status = 'COMPLETED_NO_CHANGES'  # Default status

        try:
            tiles = db.session.query(ImageTile).filter_by(area_config_id=area_config_id).order_by(
                ImageTile.capture_time.desc()).all()

            tiles_by_unique_key = {}
            for tile in tiles:
                if tile.unique_key not in tiles_by_unique_key:
                    tiles_by_unique_key[tile.unique_key] = []
                tiles_by_unique_key[tile.unique_key].append(tile)

            for unique_key, tile_list in tiles_by_unique_key.items():
                if len(tile_list) >= 2:
                    latest_tile = tile_list[0]  # Most recent capture
                    previous_tile = tile_list[1]  # Second most recent capture

                    print(
                        f"Comparing uniqueKey: {unique_key}, Latest: {latest_tile.image_path}, Previous: {previous_tile.image_path}")

                    # Pass app_config to compare_images
                    comparison_result = ImageComparisonService.compare_images(previous_tile.image_path,
                                                                              latest_tile.image_path, app_config)

                    latest_tile.last_comparison_time = datetime.utcnow()
                    latest_tile.change_detected = comparison_result['changed']
                    latest_tile.status = 'CHANGED' if comparison_result['changed'] else 'NO_CHANGE'

                    db.session.add(latest_tile)  # Update the existing latest_tile object

                    if comparison_result['changed']:
                        total_changes_in_session += 1
                        session_status = 'COMPLETED_CHANGES_DETECTED'
                        print(
                            f"ALERT: Change detected for tile {unique_key} (Area: {area_config_id})! Change: {comparison_result['change_percent']}%")

                        # --- Log Alert Detail ---
                        alert_detail = AlertDetail(
                            alert_session_id=alert_session.id,
                            image_tile_id=latest_tile.id,
                            previous_image_path=previous_tile.image_path,
                            current_image_path=latest_tile.image_path,
                            change_log=json.dumps(comparison_result),  # Store as JSON string
                            alert_time=datetime.utcnow()
                        )
                        db.session.add(alert_detail)
                        # --- End Log Alert Detail ---

                elif len(tile_list) == 1:
                    print(f"Only one image found for unique key {unique_key}. Cannot perform comparison.")
                    tile_list[0].status = 'CAPTURED'  # Or INITIAL
                    db.session.add(tile_list[0])
                else:
                    print(f"No images found for unique key {unique_key}.")

                db.session.commit()  # Commit after each tile update/alert detail log for atomicity

        except Exception as e:
            session_status = 'COMPLETED_ERROR'
            print(f"Error during comparison run for AreaConfig {area_config_id}: {e}")
            db.session.rollback()  # Rollback any pending changes on error

        finally:
            # --- Finalize Alert Session ---
            alert_session.end_time = datetime.utcnow()
            alert_session.total_changes_detected = total_changes_in_session
            alert_session.status = session_status
            db.session.add(alert_session)  # Add back to session in case of rollback above
            db.session.commit()

            # --- Trigger Firebase Notification ---
            FirebaseService.initialize_firebase()  # Ensure Firebase is initialized
            if total_changes_in_session > 0:
                title = f"Land Change Alert for {area_config_id}"
                body = f"Detected {total_changes_in_session} changes in area {area_config_id}."
                data_payload = {
                    "area_config_id": str(area_config_id),
                    "alert_session_id": str(alert_session.id),
                    "changes_count": str(total_changes_in_session)
                }
                # app_config contains FCM_DEFAULT_DEVICE_TOKEN
                fcm_token = app_config.get('FCM_DEFAULT_DEVICE_TOKEN')
                if fcm_token:
                    FirebaseService.send_notification(title, body, device_token=fcm_token, data_payload=data_payload)
                else:
                    print("Warning: FCM_DEFAULT_DEVICE_TOKEN not set in config, notification not sent.")
            else:
                print(f"No changes detected for area {area_config_id}. No notification sent.")

        print(f"Finished image comparison for AreaConfig ID: {area_config_id}")

