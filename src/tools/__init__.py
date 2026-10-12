"""Orchestrated backend tools for LogiAgent."""
from src.tools.tracking_tool import track_shipment
from src.tools.eta_tool import calculate_eta_and_distance
from src.tools.issue_tool import report_shipment_issue
from src.tools.support_tool import get_customer_support_info

LOGISTICS_TOOLS = [
    track_shipment,
    calculate_eta_and_distance,
    report_shipment_issue,
    get_customer_support_info,
]

__all__ = [
    "track_shipment",
    "calculate_eta_and_distance",
    "report_shipment_issue",
    "get_customer_support_info",
    "LOGISTICS_TOOLS",
]
