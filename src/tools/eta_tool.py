import json
from langchain_core.tools import tool
from src.database.connection import get_db_session
from src.database.models import Shipment
from src.utils.geo import haversine_distance, calculate_eta


@tool
def calculate_eta_and_distance(tracking_number: str) -> str:
    """
    Computes geodesic distance and estimated time of arrival (ETA) for a shipment
    using live GPS coordinates and destination coordinates via the Haversine formula.

    :param tracking_number: Tracking code of the parcel (e.g., 'PKG-1001').
    :return: JSON formatted string containing distance, speed, remaining hours/minutes, and arrival timestamp.
    """
    clean_tracking = tracking_number.strip().upper()
    with get_db_session() as db:
        shipment = (
            db.query(Shipment)
            .filter(Shipment.tracking_number == clean_tracking)
            .first()
        )
        if not shipment:
            return json.dumps({
                "status": "NOT_FOUND",
                "message": f"Cannot calculate ETA. Shipment '{tracking_number}' not found."
            })

        if shipment.status == "DELIVERED":
            return json.dumps({
                "status": "DELIVERED",
                "tracking_number": shipment.tracking_number,
                "message": "Shipment has already been delivered to the final destination.",
                "remaining_distance_km": 0.0,
                "eta": "0h 00m",
            })

        # Calculate Haversine geodesic distance from live GPS to Destination
        distance_km = haversine_distance(
            lat1=shipment.current_lat,
            lon1=shipment.current_lon,
            lat2=shipment.dest_lat,
            lon2=shipment.dest_lon,
        )

        # Carrier transit speed
        carrier_speed = shipment.carrier.avg_speed_kmh if shipment.carrier else 65.0

        # Delay factor if status is DELAYED
        delay_hours = 2.0 if shipment.status == "DELAYED" else 0.0

        eta_info = calculate_eta(
            distance_km=distance_km,
            speed_kmh=carrier_speed,
            delay_hours=delay_hours,
        )

        response = {
            "tracking_number": shipment.tracking_number,
            "status": shipment.status,
            "carrier": shipment.carrier.name if shipment.carrier else "Unknown",
            "current_location": shipment.current_location_name,
            "current_coordinates": {
                "latitude": shipment.current_lat,
                "longitude": shipment.current_lon,
            },
            "destination_city": shipment.dest_city,
            "destination_coordinates": {
                "latitude": shipment.dest_lat,
                "longitude": shipment.dest_lon,
            },
            "remaining_distance_km": eta_info["distance_km"],
            "remaining_distance_miles": eta_info["distance_miles"],
            "transit_speed_kmh": eta_info["speed_kmh"],
            "estimated_transit_time": eta_info["eta_formatted"],
            "estimated_arrival": eta_info["estimated_arrival"],
        }
        return json.dumps(response, indent=2)
