import pytest
from src.utils.geo import haversine_distance


def test_haversine_known_coordinates():
    """
    Test 1: Verifies geodesic distance between New York and Los Angeles
    against known theoretical distance (~3935.7 km) with <0.5% tolerance.
    """
    ny_lat, ny_lon = 40.7128, -74.0060
    la_lat, la_lon = 34.0522, -118.2437

    distance = haversine_distance(ny_lat, ny_lon, la_lat, la_lon)

    # Expected distance is ~3935.7 km
    assert 3920.0 <= distance <= 3950.0
    assert isinstance(distance, float)


def test_haversine_same_coordinates_zero_distance():
    """
    Test 2: Verifies that distance between identical coordinates is exactly 0.0 km.
    """
    lat, lon = 41.8781, -87.6298  # Chicago, IL
    distance = haversine_distance(lat, lon, lat, lon)
    assert distance == 0.0


def test_haversine_invalid_coordinates_raises_error():
    """
    Test 3: Verifies that latitude or longitude outside acceptable bounds raises ValueError.
    """
    # Latitude out of bounds (> 90)
    with pytest.raises(ValueError, match="latitude"):
        haversine_distance(95.0, 0.0, 10.0, 10.0)

    # Longitude out of bounds (< -180)
    with pytest.raises(ValueError, match="longitude"):
        haversine_distance(10.0, -195.0, 10.0, 10.0)

    # Non-numeric input raises TypeError
    with pytest.raises(TypeError):
        haversine_distance("invalid", 0.0, 10.0, 10.0)
