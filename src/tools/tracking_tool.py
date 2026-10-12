import json
from langchain_core.tools import tool
from src.database.connection import get_db_session
from src.database.models import Shipment


@tool
def track_shipment(tracking_number: str) -> str:
    """
    Look up real-time tracking details, current status, carrier, and GPS checkpoint history for a shipment.
    
    :param tracking_number: Tracking code of the parcel (e.g., 'PKG-1001').
    :return: JSON formatted string containing current status and coordinates.
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
                "message": f"No shipment found matching tracking number '{tracking_number}'."
            })

        checkpoints_data = [
            {
                "timestamp": cp.timestamp.isoformat() if cp.timestamp else None,
                "location": cp.location_name,
                "lat": cp.lat,
                "lon": cp.lon,
                "note": cp.status_note,
            }
            for cp in sorted(shipment.checkpoints, key=lambda c: c.timestamp or 0)
        ]

        result = {
            "tracking_number": shipment.tracking_number,
            "carrier": shipment.carrier.name if shipment.carrier else "Unknown",
            "carrier_code": shipment.carrier.code if shipment.carrier else "N/A",
            "status": shipment.status,
            "origin": {
                "city": shipment.origin_city,
                "lat": shipment.origin_lat,
                "lon": shipment.origin_lon,
            },
            "destination": {
                "city": shipment.dest_city,
                "lat": shipment.dest_lat,
                "lon": shipment.dest_lon,
            },
            "current_location": {
                "name": shipment.current_location_name,
                "lat": shipment.current_lat,
                "lon": shipment.current_lon,
            },
            "last_updated": shipment.updated_at.isoformat() if shipment.updated_at else None,
            "checkpoint_history": checkpoints_data,
        }
        return json.dumps(result, indent=2)
