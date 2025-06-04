from math import radians, cos
import numpy as np

class GeoUtils:
    EARTH_RADIUS_METERS = 6371000.0

    @staticmethod
    def meters_to_latitude_degrees(meters):
        return meters / (GeoUtils.EARTH_RADIUS_METERS * (np.pi / 180.0))

    @staticmethod
    def meters_to_longitude_degrees(meters, latitude):
        radians_lat = radians(latitude)
        return meters / (GeoUtils.EARTH_RADIUS_METERS * cos(radians_lat) * (np.pi / 180.0))

    @staticmethod
    def calculate_bounding_box(center_lat, center_lon, north_km, south_km, east_km, west_km):
        north_meters = north_km * 1000
        south_meters = south_km * 1000
        east_meters = east_km * 1000
        west_meters = west_km * 1000

        min_lat = center_lat - GeoUtils.meters_to_latitude_degrees(south_meters)
        max_lat = center_lat + GeoUtils.meters_to_latitude_degrees(north_meters)
        min_lon = center_lon - GeoUtils.meters_to_longitude_degrees(west_meters, center_lat)
        max_lon = center_lon + GeoUtils.meters_to_longitude_degrees(east_meters, center_lat)

        return {'minLat': min_lat, 'maxLat': max_lat, 'minLon': min_lon, 'maxLon': max_lon}
