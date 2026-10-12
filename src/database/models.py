from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(30), nullable=False)
    address = Column(String(250), nullable=False)

    shipments = relationship("Shipment", back_populates="customer")


class Carrier(Base):
    __tablename__ = "carriers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    support_phone = Column(String(30), nullable=False)
    support_email = Column(String(120), nullable=False)
    avg_speed_kmh = Column(Float, default=65.0, nullable=False)

    shipments = relationship("Shipment", back_populates="carrier")


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tracking_number = Column(String(50), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    carrier_id = Column(Integer, ForeignKey("carriers.id"), nullable=False)

    status = Column(String(30), default="IN_TRANSIT", nullable=False)
    # Origin & Destination GPS
    origin_city = Column(String(100), nullable=False)
    origin_lat = Column(Float, nullable=False)
    origin_lon = Column(Float, nullable=False)

    dest_city = Column(String(100), nullable=False)
    dest_lat = Column(Float, nullable=False)
    dest_lon = Column(Float, nullable=False)

    # Live GPS coordinates stream simulation
    current_lat = Column(Float, nullable=False)
    current_lon = Column(Float, nullable=False)
    current_location_name = Column(String(120), nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    customer = relationship("Customer", back_populates="shipments")
    carrier = relationship("Carrier", back_populates="shipments")
    checkpoints = relationship(
        "TrackingCheckpoint", back_populates="shipment", cascade="all, delete-orphan"
    )
    issues = relationship(
        "ShipmentIssue", back_populates="shipment", cascade="all, delete-orphan"
    )


class TrackingCheckpoint(Base):
    __tablename__ = "tracking_checkpoints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    location_name = Column(String(120), nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status_note = Column(String(200), nullable=False)

    shipment = relationship("Shipment", back_populates="checkpoints")


class ShipmentIssue(Base):
    __tablename__ = "shipment_issues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    issue_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(30), default="OPEN", nullable=False)
    reported_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    shipment = relationship("Shipment", back_populates="issues")
