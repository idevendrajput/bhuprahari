import os
import requests
from datetime import datetime
from math import ceil
from extensions import db  # Import db from extensions
from entities.models import ImageTile  # Import ImageTile model
from utils.geo_utils import GeoUtils  # Import GeoUtils


class ImageCaptureService:
    TILE_SIZE_METERS = 236.0  # Changed from 50.0 to 100.0 to match zoom=20's ~116m coverage more practically

    @staticmethod
    # Accept app_config as an argument
    def download_and_save_image(area_config_id, lat, lon, unique_key, app_config):
        image_url = (
            f"{app_config['Maps_STATIC_URL']}?"  # Use app_config
            f"center={lat},{lon}&zoom={app_config['Maps_IMAGE_ZOOM']}&"  # Use app_config
            f"size={app_config['Maps_IMAGE_SIZE']}&maptype=satellite&key={app_config['Maps_API_KEY']}"  # Use app_config
        )
        current_timestamp = datetime.utcnow()
        file_name = f"{unique_key}_{current_timestamp.strftime('%Y%m%d%H%M%S')}.png"

        area_image_dir = os.path.join(app_config['IMAGE_STORAGE_DIRECTORY'], str(area_config_id))  # Use app_config
        os.makedirs(area_image_dir, exist_ok=True)
        file_path = os.path.join(area_image_dir, file_name)

        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Image saved: {file_path}")

            new_tile = ImageTile(
                area_config_id=area_config_id,
                unique_key=unique_key,
                latitude=lat,
                longitude=lon,
                capture_time=current_timestamp,
                image_path=file_path,
                status='CAPTURED'
            )
            db.session.add(new_tile)
            db.session.commit()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image from {image_url}: {e}")
            return False
        except Exception as e:
            print(f"Error saving image or updating DB for unique key {unique_key}: {e}")
            db.session.rollback()  # Rollback on error
            return False

    @staticmethod
    # Accept app_config as an argument
    def capture_images_for_area(area_config, app_config):
        print(f"Starting image capture for AreaConfig ID: {area_config.id}, Name: {area_config.name}")

        bbox = GeoUtils.calculate_bounding_box(
            area_config.center_lat, area_config.center_lon,
            area_config.north_km, area_config.south_km,
            area_config.east_km, area_config.west_km
        )

        lat_diff_meters = (area_config.north_km + area_config.south_km) * 1000
        lon_diff_meters = (area_config.east_km + area_config.west_km) * 1000

        num_lat_tiles = ceil(lat_diff_meters / ImageCaptureService.TILE_SIZE_METERS)
        num_lon_tiles = ceil(lon_diff_meters / ImageCaptureService.TILE_SIZE_METERS)

        print(
            f"Area spans approx {lat_diff_meters}m (lat) x {lon_diff_meters}m (lon). Will generate {int(num_lat_tiles)}x{int(num_lon_tiles)} tiles.")

        for i in range(int(num_lat_tiles)):
            for j in range(int(num_lon_tiles)):
                current_lat = bbox['minLat'] + GeoUtils.meters_to_latitude_degrees(
                    i * ImageCaptureService.TILE_SIZE_METERS + ImageCaptureService.TILE_SIZE_METERS / 2.0)
                current_lon = bbox['minLon'] + GeoUtils.meters_to_longitude_degrees(
                    j * ImageCaptureService.TILE_SIZE_METERS + ImageCaptureService.TILE_SIZE_METERS / 2.0, current_lat)

                unique_key = f"{area_config.id}_{current_lat:.6f}_{current_lon:.6f}".replace('.', '_')

                # Pass app_config to download_and_save_image
                ImageCaptureService.download_and_save_image(area_config.id, current_lat, current_lon, unique_key,
                                                            app_config)

        print(f"Finished image capture for AreaConfig ID: {area_config.id}")
