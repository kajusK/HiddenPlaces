"""Integration tests for app.utils. """
from app.utils import GeoIp


def test_geo_ip():
    """Test the GeoIp info fetching. """
    info = GeoIp('8.8.8.8')
    assert info.valid
    assert info.country == "United States"
    assert info.country_code == "US"
