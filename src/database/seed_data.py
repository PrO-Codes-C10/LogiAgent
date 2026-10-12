from datetime import datetime, timezone, timedelta
from src.database.connection import init_db, get_db_session
from src.database.models import Customer, Carrier, Shipment, TrackingCheckpoint, ShipmentIssue


def seed_database():
    """Initializes schema and populates sample logistics data."""
    init_db()

    with get_db_session() as db:
        # Check if already seeded
        if db.query(Shipment).first() is not None:
            return

        # 1. Carriers
        fedex = Carrier(
            name="FedEx Express",
            code="FDX",
            support_phone="+1-800-463-3339",
            support_email="support@fedex.com",
            avg_speed_kmh=75.0,
        )
        ups = Carrier(
            name="UPS Freight",
            code="UPS",
            support_phone="+1-800-742-5877",
            support_email="customer.care@ups.com",
            avg_speed_kmh=65.0,
        )
        dhl = Carrier(
            name="DHL Express",
            code="DHL",
            support_phone="+1-800-225-5345",
            support_email="help@dhl.com",
            avg_speed_kmh=70.0,
        )
        db.add_all([fedex, ups, dhl])
        db.flush()

        # 2. Customers
        alice = Customer(
            name="Alice Johnson",
            email="alice.johnson@example.com",
            phone="+1 (555) 349-8812",
            address="742 Evergreen Terrace, Springfield, IL 62704",
        )
        bob = Customer(
            name="Bob Smith",
            email="bob.smith@corporate.org",
            phone="+1 (555) 782-9901",
            address="1004 Elm Street, Apt 4B, Chicago, IL 60601",
        )
        carlos = Customer(
            name="Carlos Mendez",
            email="carlos.mendez@mail.net",
            phone="+1 (555) 412-6534",
            address="88 Ocean Drive, Suite 12, Miami, FL 33139",
        )
        diana = Customer(
            name="Diana Prince",
            email="diana.prince@themyscira.com",
            phone="+1 (555) 901-2244",
            address="350 5th Avenue, New York, NY 10118",
        )
        db.add_all([alice, bob, carlos, diana])
        db.flush()

        now = datetime.now(timezone.utc)

        # 3. Shipments
        pkg_1001 = Shipment(
            tracking_number="PKG-1001",
            customer_id=alice.id,
            carrier_id=fedex.id,
            status="IN_TRANSIT",
            origin_city="New York, NY",
            origin_lat=40.7128,
            origin_lon=-74.0060,
            dest_city="Chicago, IL",
            dest_lat=41.8781,
            dest_lon=-87.6298,
            current_lat=41.4993,
            current_lon=-81.6944,
            current_location_name="Cleveland, OH Distribution Hub",
            created_at=now - timedelta(days=2),
        )

        pkg_1002 = Shipment(
            tracking_number="PKG-1002",
            customer_id=bob.id,
            carrier_id=ups.id,
            status="OUT_FOR_DELIVERY",
            origin_city="Detroit, MI",
            origin_lat=42.3314,
            origin_lon=-83.0458,
            dest_city="Chicago, IL",
            dest_lat=41.8781,
            dest_lon=-87.6298,
            current_lat=41.8820,
            current_lon=-87.6320,
            current_location_name="Chicago Loop Delivery Van 42",
            created_at=now - timedelta(days=1),
        )

        pkg_1003 = Shipment(
            tracking_number="PKG-1003",
            customer_id=carlos.id,
            carrier_id=dhl.id,
            status="DELAYED",
            origin_city="Atlanta, GA",
            origin_lat=33.7490,
            origin_lon=-84.3880,
            dest_city="Miami, FL",
            dest_lat=25.7617,
            dest_lon=-80.1918,
            current_lat=28.5383,
            current_lon=-81.3792,
            current_location_name="Orlando, FL Sorting Facility",
            created_at=now - timedelta(days=3),
        )

        pkg_1004 = Shipment(
            tracking_number="PKG-1004",
            customer_id=diana.id,
            carrier_id=fedex.id,
            status="DELIVERED",
            origin_city="Los Angeles, CA",
            origin_lat=34.0522,
            origin_lon=-118.2437,
            dest_city="New York, NY",
            dest_lat=40.7128,
            dest_lon=-74.0060,
            current_lat=40.7128,
            current_lon=-74.0060,
            current_location_name="Delivered to Front Desk, New York",
            created_at=now - timedelta(days=5),
        )

        db.add_all([pkg_1001, pkg_1002, pkg_1003, pkg_1004])
        db.flush()

        # 4. Checkpoints
        cp1 = TrackingCheckpoint(
            shipment_id=pkg_1001.id,
            location_name="New York Origin Depot",
            lat=40.7128,
            lon=-74.0060,
            timestamp=now - timedelta(days=2),
            status_note="Parcel scanned and departed origin hub",
        )
        cp2 = TrackingCheckpoint(
            shipment_id=pkg_1001.id,
            location_name="Scranton, PA Sorting Station",
            lat=41.4090,
            lon=-75.6624,
            timestamp=now - timedelta(days=1, hours=8),
            status_note="In transit through regional logistics waypoint",
        )
        cp3 = TrackingCheckpoint(
            shipment_id=pkg_1001.id,
            location_name="Cleveland, OH Distribution Hub",
            lat=41.4993,
            lon=-81.6944,
            timestamp=now - timedelta(hours=3),
            status_note="Scanned into intermediate sorting conveyor",
        )

        cp4 = TrackingCheckpoint(
            shipment_id=pkg_1002.id,
            location_name="Chicago South Hub",
            lat=41.8300,
            lon=-87.6500,
            timestamp=now - timedelta(hours=5),
            status_note="Sorted onto local delivery truck route #19",
        )

        cp5 = TrackingCheckpoint(
            shipment_id=pkg_1003.id,
            location_name="Orlando, FL Sorting Facility",
            lat=28.5383,
            lon=-81.3792,
            timestamp=now - timedelta(hours=14),
            status_note="Transit held due to thunderstorm warning",
        )

        db.add_all([cp1, cp2, cp3, cp4, cp5])

        # 5. Issues
        issue1 = ShipmentIssue(
            shipment_id=pkg_1003.id,
            issue_type="DELAYED",
            description="Severe convective storm alert along I-95 south corridor; delivery postponed 24h.",
            status="OPEN",
            reported_at=now - timedelta(hours=12),
        )
        db.add(issue1)


if __name__ == "__main__":
    seed_database()
    print("Database successfully initialized and seeded!")
