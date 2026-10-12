import json
from langchain_core.tools import tool
from src.database.connection import get_db_session
from src.database.models import Shipment, ShipmentIssue


@tool
def report_shipment_issue(tracking_number: str, issue_type: str, description: str) -> str:
    """
    Report an issue or exception with a shipment (e.g. DAMAGED, DELAYED, LOST, WRONG_ADDRESS)
    and create a tracking support ticket in the database.

    :param tracking_number: Tracking code of the parcel (e.g., 'PKG-1001').
    :param issue_type: Category of issue ('DAMAGED', 'DELAYED', 'LOST', 'WRONG_ADDRESS', 'OTHER').
    :param description: Detailed explanation of the customer complaint or exception.
    :return: JSON formatted string confirming ticket creation and status update.
    """
    clean_tracking = tracking_number.strip().upper()
    valid_types = {"DAMAGED", "DELAYED", "LOST", "WRONG_ADDRESS", "OTHER"}
    normalized_type = issue_type.strip().upper()
    if normalized_type not in valid_types:
        normalized_type = "OTHER"

    with get_db_session() as db:
        shipment = (
            db.query(Shipment)
            .filter(Shipment.tracking_number == clean_tracking)
            .first()
        )
        if not shipment:
            return json.dumps({
                "status": "NOT_FOUND",
                "message": f"Cannot report issue. Shipment '{tracking_number}' not found."
            })

        # Create issue record
        new_issue = ShipmentIssue(
            shipment_id=shipment.id,
            issue_type=normalized_type,
            description=description.strip(),
            status="OPEN",
        )
        db.add(new_issue)

        # Update shipment status if critical
        if normalized_type in {"DELAYED", "DAMAGED", "LOST"}:
            shipment.status = "DELAYED" if normalized_type == "DELAYED" else "EXCEPTION"

        db.flush()

        response = {
            "ticket_id": f"TICK-{new_issue.id:04d}",
            "tracking_number": shipment.tracking_number,
            "issue_type": normalized_type,
            "description": description.strip(),
            "status": "OPEN",
            "shipment_current_status": shipment.status,
            "message": "Incident ticket registered successfully. A logistics support specialist has been notified.",
        }
        return json.dumps(response, indent=2)
