import json
from langchain_core.tools import tool
from src.database.connection import get_db_session
from src.database.models import Shipment
from src.utils.pii_masker import mask_pii_dict


@tool
def get_customer_support_info(tracking_number: str) -> str:
    """
    Retrieve carrier contact assistance and recipient details for a shipment,
    strictly masked with PII-protection algorithms to preserve privacy.

    :param tracking_number: Tracking code of the parcel (e.g., 'PKG-1001').
    :return: JSON formatted string containing carrier helpline and PII-masked recipient data.
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
                "message": f"Cannot fetch support info. Shipment '{tracking_number}' not found."
            })

        carrier = shipment.carrier
        customer = shipment.customer

        raw_data = {
            "tracking_number": shipment.tracking_number,
            "carrier_name": carrier.name if carrier else "Standard Courier",
            "carrier_support_phone": carrier.support_phone if carrier else "N/A",
            "carrier_support_email": carrier.support_email if carrier else "N/A",
            "recipient_name": customer.name if customer else "Unknown",
            "recipient_email": customer.email if customer else "N/A",
            "recipient_phone": customer.phone if customer else "N/A",
            "delivery_address": customer.address if customer else "N/A",
            "security_notice": "All sensitive personal identifiable information (PII) is automatically masked.",
        }

        # Apply PII masking to safeguard customer data
        masked_data = mask_pii_dict(raw_data)
        return json.dumps(masked_data, indent=2)
