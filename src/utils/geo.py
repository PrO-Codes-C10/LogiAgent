import math
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

EARTH_RADIUS_KM = 6371.0


def validate_coordinates(lat: float, lon: float, label: str = "Coordinates") -> None:
    """Validates that latitude is within [-90, 90] and longitude is within [-180, 180]."""
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        raise TypeError(f"{label} latitude and longitude must be numeric.")
    if not (-90.0 <= lat <= 90.0):
        raise ValueError(f"{label} latitude {lat} is out of valid bounds [-90, 90].")
    if not (-180.0 <= lon <= 180.0):
        raise ValueError(f"{label} longitude {lon} is out of valid bounds [-180, 180].")


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two GPS coordinates using Haversine formula.

    Returns distance in kilometers rounded to 2 decimal places.
    """
    validate_coordinates(lat1, lon1, label="Origin")
    validate_coordinates(lat2, lon2, label="Destination")

    # If coordinates are identical, return 0.0 directly
    if lat1 == lat2 and lon1 == lon2:
        return 0.0

    # Convert degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine core formula
    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )

    # Clamp to handle numerical rounding
    a = min(1.0, max(0.0, a))

    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    distance = EARTH_RADIUS_KM * c

    return round(distance, 2)


def calculate_eta(
    distance_km: float,
    speed_kmh: float = 65.0,
    delay_hours: float = 0.0,
    base_time: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Computes remaining transit time and estimated arrival timestamp.

    :param distance_km: Remaining travel distance in kilometers (>= 0).
    :param speed_kmh: Average vehicle transit speed in km/h (> 0).
    :param delay_hours: Optional known delays due to traffic/weather.
    :param base_time: Reference start time (defaults to current UTC time).
    :return: Dictionary containing distance, hours, minutes, and arrival timestamp.
    """
    if distance_km < 0:
        raise ValueError("Distance cannot be negative.")
    if speed_kmh <= 0:
        raise ValueError("Speed must be strictly greater than 0.")
    if delay_hours < 0:
        raise ValueError("Delay hours cannot be negative.")

    if base_time is None:
        base_time = datetime.now(timezone.utc)
    elif base_time.tzinfo is None:
        base_time = base_time.replace(tzinfo=timezone.utc)

    # Compute total hours
    raw_transit_hours = (distance_km / speed_kmh) + delay_hours
    total_minutes = int(round(raw_transit_hours * 60))

    hours = total_minutes // 60
    minutes = total_minutes % 60

    estimated_arrival_dt = base_time + timedelta(minutes=total_minutes)
    distance_miles = round(distance_km * 0.621371, 2)

    return {
        "distance_km": round(distance_km, 2),
        "distance_miles": distance_miles,
        "speed_kmh": round(speed_kmh, 1),
        "delay_hours": round(delay_hours, 2),
        "total_transit_hours": round(raw_transit_hours, 2),
        "hours": hours,
        "minutes": minutes,
        "eta_formatted": f"{hours}h {minutes:02d}m",
        "estimated_arrival": estimated_arrival_dt.isoformat(),
    }
