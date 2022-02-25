from unittest.mock import patch, mock_open
from pytest import approx, raises
from urllib.error import URLError
from app.utils.geolocation import GeoIp, LatLon


def test_geo_ip_full():
    """Tests the GeoIp info fetching when all fields are set. """
    data = '{"country_code":"CZ","country_name":"Czechia",' \
           '"city":"Prague","postal":"120 00","latitude":50.0761,' \
           '"longitude":14.4477,"IPv4":"1.2.3.4",' \
           '"state":"Hlavni mesto Praha"}'
    mopen = mock_open(read_data=data.encode('utf-8'))

    with patch('app.utils.geolocation.urllib.request.urlopen', mopen) as mock:
        info = GeoIp('1.2.3.4')

    mock.assert_called_once_with("https://geolocation-db.com/json/1.2.3.4")
    assert info.valid
    assert info.country == "Czechia"
    assert info.country_code == "CZ"
    assert info.city == "Prague"
    assert info.lat == 50.0761
    assert info.lon == 14.4477


def test_geo_ip_partial():
    """Tests the GeoIp info fetching when not all fields are set. """
    data = '{"country_code":"US","country_name":"United States",' \
           '"city":null,"postal":null,"latitude":37.751,"longitude":-97.822,' \
           '"IPv4":"8.8.8.8","state":null}'
    mopen = mock_open(read_data=data.encode('utf-8'))

    with patch('app.utils.geolocation.urllib.request.urlopen', mopen) as mock:
        info = GeoIp('8.8.8.8')

    mock.assert_called_once_with("https://geolocation-db.com/json/8.8.8.8")
    assert info.valid
    assert info.country == "United States"
    assert info.country_code == "US"
    assert info.city is None
    assert info.lat == 37.751
    assert info.lon == -97.822


def test_geo_ip_invalid():
    """Tests the GeoIp info fetching when receiving invalid response. """
    mopen = mock_open(read_data='crippled'.encode('utf-8'))
    with patch('app.utils.geolocation.urllib.request.urlopen', mopen):
        info = GeoIp('8.8.8.8')
    assert not info.valid
    assert info.country is None
    assert info.country_code is None
    assert info.city is None
    assert info.lat is None
    assert info.lon is None


def test_geo_ip_no_response():
    """Tests the GeoIp info fetching when remote site in unreachable. """
    mopen = mock_open(read_data='{}'.encode('utf-8'))
    with patch('app.utils.geolocation.urllib.request.urlopen', mopen) as mock_url:
        mock_url.side_effect = URLError("foo bar")
        info = GeoIp('8.8.8.8')
    assert not info.valid
    assert info.country is None
    assert info.country_code is None
    assert info.city is None
    assert info.lat is None
    assert info.lon is None


def test_latlon_conversion(subtests):
    """Tests the LatLon object creation for various coordinat formats."""
    valid = [
        # decimal degrees format
        ('40.7648N', 40.7648, True),
        ('67.7648 S', -67.7648, True),
        ('40 N', 40, True),
        ('67S', -67, True),
        ('  123.7648  E  ', 123.7684, False),
        ('168.7648W', -168.7648, False),
        # degrees, decimal minutes format
        ('15°24.15\'N', 15.4025, True),
        ('0 ° 18.15 \'S', -0.3025, True),
        ('131°24.92\'E', 131.4153, False),
        ('1°51.75\'  W ', -1.8625, False),
        # degrees, minutes, seconds format
        ('15°24\'15.2"N', 15.404222, True),
        ('86 °  5 \' 1 " S ', -86.0836, True),
        ('15°24\'15.2"E', 15.404222, False),
        ('86 °  5 \' 1 " W ', -86.0836, False),
        # Still valid, but questionable - seconds/minutes overflow
        ('15°84\'15.2"N', 16.404222, True),
        ('15°24\'3615.2"N', 16.404222, True),
    ]
    invalid = ['foo123.456Nbar', '91.231N', '-12.345N', '40,123N', '123.1S',
               '91°24.15\'N', '89°84.15\'S', '181°24\'15.2"E',
               '181°24\'15.2"W', '18°24.15N', '18°24\'15.2E']

    for item in valid:
        with subtests.test(data=item[0]):
            result = LatLon.from_str(item[0])
            assert result.is_latitude is item[2]
            assert result.is_longitude is not item[2]
            assert result.value == approx(item[1], 1e-4)

    for item in invalid:
        with subtests.test(data=item):
            with raises(ValueError):
                LatLon.from_str(item)


def test_latlon_to_decimal_str(subtests):
    """Tests conversion of LatLon object to decimal string."""
    items = [
        (LatLon(12.654, True), '12.654000N'),
        (LatLon(-12.654, True), '12.654000S'),
        (LatLon(123.456, False), '123.456000E'),
        (LatLon(-123.456, False), '123.456000W'),
    ]

    for item in items:
        with subtests.test(expected=item[1]):
            assert item[0].toDecimalStr() == item[1]


def test_latlon_str(subtests):
    """Tests conversion of LatLon object to string."""
    items = [
        (LatLon(12.654, True), '12°39\'14.4" N'),
        (LatLon(-12.654, True), '12°39\'14.4" S'),
        (LatLon(123.456, False), '123°27\'21.6" E'),
        (LatLon(-123.456, False), '123°27\'21.6" W'),
    ]

    for item in items:
        with subtests.test(expected=item[1]):
            assert str(item[0]) == item[1]
