from datetime import datetime, timezone, timedelta
import pytest
from src.utils.geo import calculate_eta


def test_calculate_eta_standard():
    """
    Test 4: Verifies standard ETA calculation given distance and vehicle speed.
    130 km at 65 km/h = exactly 2 hours (120 minutes).
    """
    base_time = datetime(2026, 10, 11, 12, 0, 0, tzinfo=timezone.utc)
    eta_result = calculate_eta(distance_km=130.0, speed_kmh=65.0, delay_hours=0.0, base_time=base_time)

    assert eta_result["distance_km"] == 130.0
    assert eta_result["hours"] == 2
    assert eta_result["minutes"] == 0
    assert eta_result["eta_formatted"] == "2h 00m"
    assert eta_result["total_transit_hours"] == 2.0


def test_calculate_eta_invalid_inputs():
    """
    Test 5: Verifies that non-positive speed or negative distance raises ValueError.
    """
    with pytest.raises(ValueError, match="Speed must be strictly greater than 0"):
        calculate_eta(distance_km=100.0, speed_kmh=0.0)

    with pytest.raises(ValueError, match="Speed must be strictly greater than 0"):
        calculate_eta(distance_km=100.0, speed_kmh=-20.0)

    with pytest.raises(ValueError, match="Distance cannot be negative"):
        calculate_eta(distance_km=-15.0, speed_kmh=60.0)


def test_calculate_eta_future_timestamp_with_delay():
    """
    Test 6: Verifies that estimated arrival timestamp correctly integrates transit hours + delay factor.
    """
    base_time = datetime(2026, 10, 11, 10, 0, 0, tzinfo=timezone.utc)
    # 75 km at 50 km/h = 1.5 hours + 1.0 hour delay = 2.5 hours (2h 30m)
    eta_result = calculate_eta(distance_km=75.0, speed_kmh=50.0, delay_hours=1.0, base_time=base_time)

    assert eta_result["hours"] == 2
    assert eta_result["minutes"] == 30
    assert eta_result["eta_formatted"] == "2h 30m"

    expected_arrival = base_time + timedelta(hours=2, minutes=30)
    assert eta_result["estimated_arrival"] == expected_arrival.isoformat()
