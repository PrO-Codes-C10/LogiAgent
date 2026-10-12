"""LogiAgent - AI-Powered Logistics & Shipment Tracking Agent.

Interactive terminal CLI and automated demonstration script.
"""

import sys
import argparse
from src.database.seed_data import seed_database
from src.agent.orchestrator import LogiAgentOrchestrator


def print_banner():
    banner = r"""
================================================================================
  _                 _      _                    _   
 | |   ___  __ _ (_)    / \   __ _  ___ _ __ | |_ 
 | |  / _ \/ _` || |   / _ \ / _` |/ _ \ '_ \| __|
 | |__| (_) \__, || |  / ___ \ (_| |  __/ | | | |_ 
 |_____\___/|___/ |_| /_/   \_\__, |\___|_| |_|\__|
                              |___/                
 AI-Powered Logistics & Real-Time Shipment Tracking Agent
================================================================================
"""
    print(banner)


def run_automated_demo(agent: LogiAgentOrchestrator):
    print("\n[+] Running Automated Orchestration Showcase across all 4 Tools:\n")
    sample_queries = [
        ("Tool 1 - Live Status & Checkpoints", "Where is shipment PKG-1001 right now?"),
        ("Tool 2 - Geodesic Distance & ETA Computation", "What is the ETA and remaining distance for PKG-1001?"),
        ("Tool 3 - Exception & Issue Ticket Logging", "My package PKG-1002 arrived damaged, please file a complaint."),
        ("Tool 4 - Customer Support & PII-Masked Dispatch", "What is the recipient and carrier support info for PKG-1004?"),
    ]

    for label, query in sample_queries:
        print("-" * 80)
        print(f">> QUERY [{label}]:")
        print(f"   \"{query}\"")
        print("\n>> AGENT EXECUTION & TOOL ORCHESTRATION:")
        res = agent.run(query)
        tool_used = res.get("tool_used")
        if tool_used:
            print(f"   * Dispatched Tool : {tool_used}")
            print(f"   * Tool Parameters : {res.get('tool_input')}")
        print("\n>> AGENT RESPONSE:")
        for line in res["answer"].splitlines():
            print(f"   {line}")
        print()


def interactive_session(agent: LogiAgentOrchestrator):
    print("\n[+] Sample tracking numbers available in database:")
    print("    - PKG-1001 (In Transit: NY -> Chicago, currently in Cleveland, OH)")
    print("    - PKG-1002 (Out for Delivery: Detroit -> Chicago Loop)")
    print("    - PKG-1003 (Delayed: Atlanta -> Miami, weather delay in Orlando, FL)")
    print("    - PKG-1004 (Delivered: LA -> New York)")
    print("\n[+] Type your questions in natural language. Type 'exit' or 'quit' to exit.\n")

    while True:
        try:
            user_input = input("LogiAgent> ").strip()
            if not user_input:
                continue
            if user_input.lower() in {"exit", "quit", "q"}:
                print("\nThank you for using LogiAgent. Goodbye!\n")
                break

            response = agent.run(user_input)
            tool_used = response.get("tool_used")
            if tool_used:
                print(f"\n[Orchestrated Tool: {tool_used}]")
            print(f"\n{response['answer']}\n")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting LogiAgent. Goodbye!")
            break


def main():
    parser = argparse.ArgumentParser(description="LogiAgent - AI-Powered Logistics Agent")
    parser.add_argument("--demo", action="store_true", help="Run automated multi-tool demonstration")
    args = parser.parse_args()

    print_banner()

    # 1. Initialize and seed database
    print("[+] Initializing database & seeding logistics telemetry...")
    seed_database()
    print("[+] Database initialized successfully.")

    # 2. Instantiate Agent Orchestrator
    agent = LogiAgentOrchestrator()

    if args.demo:
        run_automated_demo(agent)
    else:
        # If no arguments provided and stdin is non-interactive or interactive
        if not sys.stdin.isatty():
            # In automated environments, run demo
            run_automated_demo(agent)
        else:
            interactive_session(agent)


if __name__ == "__main__":
    main()
