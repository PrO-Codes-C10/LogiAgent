import os
import re
import json
from typing import Dict, Any, List, Optional
from langchain_core.tools import BaseTool

from src.tools.tracking_tool import track_shipment
from src.tools.eta_tool import calculate_eta_and_distance
from src.tools.issue_tool import report_shipment_issue
from src.tools.support_tool import get_customer_support_info
from src.config import OPENAI_API_KEY


class LogiAgentOrchestrator:
    """
    LogiAgent Orchestrator:
    Autonomous AI agent orchestrating 4 backend tools in real time
    for shipment tracking, geolocation-based ETA calculations, issue reporting,
    and PII-safe customer support queries.
    """

    SYSTEM_PROMPT = (
        "You are LogiAgent, an intelligent logistics and shipment operations assistant.\n"
        "You have access to 4 specialized real-time tools:\n"
        "1. track_shipment: Query status, carrier, and live GPS coordinates.\n"
        "2. calculate_eta_and_distance: Compute geodesic distance and arrival ETA using live GPS feeds.\n"
        "3. report_shipment_issue: Register damage, delay, or lost package tickets.\n"
        "4. get_customer_support_info: Retrieve carrier assistance and recipient details with PII masking.\n\n"
        "Always invoke the appropriate tool to retrieve ground-truth data."
    )

    def __init__(self, openai_api_key: Optional[str] = None):
        self.api_key = openai_api_key or OPENAI_API_KEY
        self.tools: List[BaseTool] = [
            track_shipment,
            calculate_eta_and_distance,
            report_shipment_issue,
            get_customer_support_info,
        ]
        self.tools_map = {tool.name: tool for tool in self.tools}
        self._llm_agent = None

        if self.api_key:
            try:
                from langchain_openai import ChatOpenAI
                from langgraph.prebuilt import create_react_agent

                model = ChatOpenAI(model="gpt-4o-mini", api_key=self.api_key, temperature=0)
                self._llm_agent = create_react_agent(model, self.tools)
            except Exception as e:
                print(f"[LogiAgent] OpenAI agent initialization skipped: {e}. Defaulting to Autonomous Deterministic Orchestration.")

    def run(self, query: str) -> Dict[str, Any]:
        """
        Processes a logistics query autonomously by identifying intent,
        dispatching backend tools, and returning synthesized responses.
        """
        # If real LLM agent is available and configured
        if self._llm_agent is not None:
            try:
                response = self._llm_agent.invoke(
                    {"messages": [("system", self.SYSTEM_PROMPT), ("user", query)]}
                )
                last_msg = response["messages"][-1]
                return {
                    "mode": "llm_react_agent",
                    "answer": last_msg.content,
                    "raw_response": response,
                }
            except Exception as err:
                print(f"[LogiAgent] LLM invocation failed ({err}). Falling back to internal orchestrator.")

        # Autonomous Semantic Orchestration Engine
        return self._autonomous_orchestrate(query)

    def _autonomous_orchestrate(self, query: str) -> Dict[str, Any]:
        """
        Autonomous orchestrator resolving intent and executing LangChain tools.
        """
        clean_query = query.strip()

        # Extract tracking number (e.g. PKG-1001 or similar patterns)
        tracking_match = re.search(r"(?i)\b(PKG[-_]?\d{4})\b", clean_query)
        tracking_number = tracking_match.group(1).upper().replace("_", "-") if tracking_match else None

        q_lower = clean_query.lower()

        # Check intent
        if not tracking_number:
            return {
                "mode": "autonomous_orchestrator",
                "tool_used": None,
                "tool_input": None,
                "tool_output": None,
                "answer": (
                    "Welcome to LogiAgent! Please provide a tracking number (e.g., PKG-1001, PKG-1002, "
                    "PKG-1003, or PKG-1004) so I can assist you with live tracking, ETA calculations, "
                    "or issue reporting."
                ),
            }

        # Intent 1: Issue Reporting / Damage / Delay
        if any(w in q_lower for w in ["damage", "broken", "issue", "problem", "complain", "lost", "missing"]):
            issue_type = "DAMAGED" if any(w in q_lower for w in ["damage", "broken"]) else "DELAYED" if "delay" in q_lower else "LOST"
            tool = self.tools_map["report_shipment_issue"]
            tool_input = {
                "tracking_number": tracking_number,
                "issue_type": issue_type,
                "description": clean_query,
            }
            raw_output = tool.invoke(tool_input)
            data = json.loads(raw_output)

            if data.get("status") == "NOT_FOUND":
                answer = f"I could not locate shipment {tracking_number} in our logistics network."
            else:
                answer = (
                    f"Support Ticket Created: {data.get('ticket_id')} for shipment {tracking_number}.\n"
                    f"- Category: {data.get('issue_type')}\n"
                    f"- Status: {data.get('status')}\n"
                    f"- Shipment State: {data.get('shipment_current_status')}\n"
                    f"- Resolution: {data.get('message')}"
                )

            return {
                "mode": "autonomous_orchestrator",
                "tool_used": "report_shipment_issue",
                "tool_input": tool_input,
                "tool_output": data,
                "answer": answer,
            }

        # Intent 2: ETA / Distance / Geolocation calculation
        elif any(w in q_lower for w in ["eta", "arrive", "arrival", "how long", "distance", "far", "time", "speed", "when"]):
            tool = self.tools_map["calculate_eta_and_distance"]
            tool_input = {"tracking_number": tracking_number}
            raw_output = tool.invoke(tool_input)
            data = json.loads(raw_output)

            if data.get("status") == "NOT_FOUND":
                answer = f"Could not calculate ETA: shipment {tracking_number} not found."
            elif data.get("status") == "DELIVERED":
                answer = f"Shipment {tracking_number} has already reached its destination and was delivered!"
            else:
                answer = (
                    f"Live Geodesic ETA Analysis for {tracking_number} ({data.get('carrier')}):\n"
                    f"- Current Location: {data.get('current_location')} "
                    f"({data.get('current_coordinates', {}).get('latitude')}, {data.get('current_coordinates', {}).get('longitude')})\n"
                    f"- Destination: {data.get('destination_city')}\n"
                    f"- Remaining Distance: {data.get('remaining_distance_km')} km ({data.get('remaining_distance_miles')} miles)\n"
                    f"- Transit Speed: {data.get('transit_speed_kmh')} km/h\n"
                    f"- Estimated Travel Time: {data.get('estimated_transit_time')}\n"
                    f"- Projected Arrival: {data.get('estimated_arrival')}"
                )

            return {
                "mode": "autonomous_orchestrator",
                "tool_used": "calculate_eta_and_distance",
                "tool_input": tool_input,
                "tool_output": data,
                "answer": answer,
            }

        # Intent 3: Support / Recipient / PII Info
        elif any(w in q_lower for w in ["support", "contact", "phone", "email", "recipient", "call", "helpline", "customer"]):
            tool = self.tools_map["get_customer_support_info"]
            tool_input = {"tracking_number": tracking_number}
            raw_output = tool.invoke(tool_input)
            data = json.loads(raw_output)

            if data.get("status") == "NOT_FOUND":
                answer = f"Could not locate customer support data for shipment {tracking_number}."
            else:
                answer = (
                    f"Customer Support & Dispatch Details for {tracking_number}:\n"
                    f"- Carrier: {data.get('carrier_name')} (Phone: {data.get('carrier_support_phone')}, Email: {data.get('carrier_support_email')})\n"
                    f"- Recipient: {data.get('recipient_name')}\n"
                    f"- Masked Contact: {data.get('recipient_phone')} | {data.get('recipient_email')}\n"
                    f"- Delivery Address: {data.get('delivery_address')}\n"
                    f"- Security Protocol: {data.get('security_notice')}"
                )

            return {
                "mode": "autonomous_orchestrator",
                "tool_used": "get_customer_support_info",
                "tool_input": tool_input,
                "tool_output": data,
                "answer": answer,
            }

        # Intent 4: Default -> Track shipment status & checkpoints
        else:
            tool = self.tools_map["track_shipment"]
            tool_input = {"tracking_number": tracking_number}
            raw_output = tool.invoke(tool_input)
            data = json.loads(raw_output)

            if data.get("status") == "NOT_FOUND":
                answer = f"Shipment {tracking_number} was not found in the tracking registry."
            else:
                checkpoints = data.get("checkpoint_history", [])
                latest_cp = checkpoints[-1]["note"] if checkpoints else "In transit"
                answer = (
                    f"Tracking Summary for {tracking_number}:\n"
                    f"- Status: {data.get('status')}\n"
                    f"- Carrier: {data.get('carrier')} (Code: {data.get('carrier_code')})\n"
                    f"- Route: {data.get('origin', {}).get('city')} -> {data.get('destination', {}).get('city')}\n"
                    f"- Current Location: {data.get('current_location', {}).get('name')}\n"
                    f"- Latest Checkpoint: {latest_cp}\n"
                    f"- Last Updated: {data.get('last_updated')}"
                )

            return {
                "mode": "autonomous_orchestrator",
                "tool_used": "track_shipment",
                "tool_input": tool_input,
                "tool_output": data,
                "answer": answer,
            }
