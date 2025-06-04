from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
# No need to import current_app here if we pass app_instance

from extensions import db  # Import db from extensions
from entities.models import AreaConfig, ImageTile
from services.image_capture_service import ImageCaptureService
from services.image_comparison_service import ImageComparisonService

scheduler = BackgroundScheduler()


# --- Scheduled Task ---
# Now accepts app_instance as an argument
def scheduled_image_monitoring(app_instance):
    with app_instance.app_context():  # Use the passed app_instance's context
        print("--- Starting scheduled image monitoring task ---")
        # Use db.session.query for database operations within the app context
        area_configs = db.session.query(AreaConfig).all()
        if not area_configs:
            print("No area configurations found to monitor.")
            return

        for config in area_configs:
            print(f"Processing AreaConfig: {config.name} (ID: {config.id})")
            try:
                # Pass app_instance.config to the service methods
                ImageCaptureService.capture_images_for_area(config, app_instance.config)
                ImageComparisonService.run_comparison_for_area(config.id, app_instance.config)
            except Exception as e:
                print(f"Error processing AreaConfig {config.id}: {e}")
        print("--- Scheduled image monitoring task finished ---")


def start_my_schedule(app_instance):  # Accept app_instance as an argument
    cron_expression = app_instance.config['SCHEDULING_CRON_EXPRESSION']

    scheduler.add_job(
        scheduled_image_monitoring,
        'cron',
        minute='*/5',  # This runs every 5th minute (0, 5, 10, etc.)
        args=[app_instance],  # Pass the app_instance as an argument to the job function
        id='image_monitoring_job',
        replace_existing=True
    )
    scheduler.start()
    print(f"Scheduler started with cron: {cron_expression}")
