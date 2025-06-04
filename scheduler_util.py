from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app

from entities.models import AreaConfig
from services.image_capture_service import ImageCaptureService
from services.image_comparison_service import ImageComparisonService

# --- Scheduled Task ---
def scheduled_image_monitoring():
    with current_app.app_context():  # Ensure this runs within the Flask application context
        print("--- Starting scheduled image monitoring task ---")
        area_configs = AreaConfig.query.all()
        if not area_configs:
            print("No area configurations found to monitor.")
            return

        for config in area_configs:
            print(f"Processing AreaConfig: {config.name} (ID: {config.id})")
            try:
                # Step 1: Capture new images
                ImageCaptureService.capture_images_for_area(config)

                # Step 2: Run comparison after capture
                ImageComparisonService.run_comparison_for_area(config.id)
            except Exception as e:
                print(f"Error processing AreaConfig {config.id}: {e}")
        print("--- Scheduled image monitoring task finished ---")


# Setup APScheduler
scheduler = BackgroundScheduler()
# Parse cron expression: "0 */5 * * * ?" -> minute=0-59/5 (every 5 minutes)
# Example: 0 0 0 */15 * ? -> Run at midnight on the 15th day of the month
# For every 5 minutes: '*/5 * * * *' (standard cron format)
# The cron format used in Spring Boot is Quartz cron, which is slightly different.
# For '0 */5 * * * ?' (Quartz cron), it means at second 0, every 5 minutes.
# APScheduler's cron trigger needs standard cron format:
# '0/5 * * * *' for every 5 minutes (at minute 0, 5, 10, ...)
# Or simpler: '*/5 * * * *' (run every 5 minutes)

# Let's use '*/5 * * * *' for every 5 minutes for demonstration
# If you want to use the exact Quartz '0 */5 * * * ?' equivalent, it would be '0 */5 * * * *' in standard cron for APScheduler
# For 15 days, it would be '0 0 0 15 * *' (at 00:00 on day 15 of every month)
# Or if you want "every 15 days from start", you'd use interval trigger or calculate it.
# Let's stick with the 'every 5 minutes' for testing.
scheduler.add_job(
    scheduled_image_monitoring,
    'cron',
    minute='*/5',  # This runs every 5th minute (0, 5, 10, etc.)
    id='image_monitoring_job',
    replace_existing=True
)