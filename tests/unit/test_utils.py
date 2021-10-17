"""Unit tests for app.utils. """
from unittest.mock import patch, mock_open
from pytest import approx, raises
from urllib.error import URLError
from flask import request
from werkzeug.datastructures import MultiDict
from app.utils import GeoIp, get_visitor_ip, random_string, LatLon, \
     OrderedEnum, StringEnum


def test_geo_ip_full():
    """Tests the GeoIp info fetching when all fields are set. """
    data = '{"country_code":"CZ","country_name":"Czechia",' \
           '"city":"Prague","postal":"120 00","latitude":50.0761,' \
           '"longitude":14.4477,"IPv4":"1.2.3.4",' \
           '"state":"Hlavni mesto Praha"}'
    mopen = mock_open(read_data=data.encode('utf-8'))

    with patch('app.utils.urllib.request.urlopen', mopen) as mock:
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

    with patch('app.utils.urllib.request.urlopen', mopen) as mock:
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
    with patch('app.utils.urllib.request.urlopen', mopen):
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
    with patch('app.utils.urllib.request.urlopen', mopen) as mock_url:
        mock_url.side_effect = URLError("foo bar")
        info = GeoIp('8.8.8.8')
    assert not info.valid
    assert info.country is None
    assert info.country_code is None
    assert info.city is None
    assert info.lat is None
    assert info.lon is None


def test_get_visitor_ip_direct(app):
    """Tests getting visitors IP when accessed directly."""
    with app.test_request_context('/'):
        # pylint: disable=assigning-non-slot
        request.remote_addr = "1.2.3.4"
        address = get_visitor_ip()
        assert address == "1.2.3.4"


def test_get_visitor_ip_proxy(app):
    """Tests getting visitors IP when accessed over reverse proxy."""
    with app.test_request_context('/'):
        # pylint: disable=assigning-non-slot
        request.remote_addr = "1.2.3.4"
        request.headers = MultiDict([('X-Forwarded-For', '8.8.8.8')])
        address = get_visitor_ip()
        assert address == "8.8.8.8"


def test_get_visitor_ip_none(app):
    """Tests getting visitors IP when accessed over reverse proxy."""
    with app.test_request_context('/'):
        # pylint: disable=assigning-non-slot
        request.remote_addr = ""
        address = get_visitor_ip()
        assert address is None


def test_random_string():
    """Tests if the function generates random strings of expected length."""
    for i in range(5, 10):
        data = []
        for j in range(10):
            output = random_string(i)
            assert len(output) == i
            data.append(output)
        assert len(set(data)) == 10


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


def test_ordered_enum(subtests):
    """Tests comparsion of OrderedEnum items."""
    class TestEnum(OrderedEnum):
        FIRST = 1
        SECOND = 2
        THIRD = 3

    class OtherEnum(OrderedEnum):
        FOO = 1
        BAR = 2

    first = TestEnum.FIRST
    second = TestEnum.SECOND
    third = TestEnum.THIRD
    other = OtherEnum.FOO

    assert first <= first
    assert first <= third
    assert first < second
    assert first < third
    assert second > first
    assert third > first
    assert second >= first
    assert second >= second

    assert not first == second
    assert not first >= third
    assert not first > second
    assert not first > third
    assert not second < first
    assert not third < first
    assert not second <= first

    with raises(TypeError):
        first < other


def test_string_enum_translation():
    """Tests enum items translations."""
    class TestEnum(StringEnum):
        FOO = 0, "translated_foo"
        BAR = 1, "translated_bar"

    assert "translated_foo" == TestEnum.FOO.translation
    assert "translated_bar" == TestEnum.BAR.translation


def test_string_enum_str():
    """Tests conversion of enum item to string value."""
    class TestEnum(StringEnum):
        FOO = 0, "translated_foo"
        BAR = 1, "translated_bar"

    assert "translated_foo" == str(TestEnum.FOO)
    assert "translated_bar" == str(TestEnum.BAR)


def test_string_enum_choices():
    """Tests getting list of enum choices for WTForms."""
    class TestEnum(StringEnum):
        FOO = 0, "translated_foo"
        BAR = 1, "translated_bar"

    data = [(0, "translated_foo"), (1, "translated_bar")]
    assert data == TestEnum.choices()


def test_string_enum_coerce():
    """Tests coercing enum items."""
    class TestEnum(StringEnum):
        FOO = 0, "translated_foo"
        BAR = 1, "translated_bar"

    assert TestEnum.coerce(TestEnum.FOO) == TestEnum.FOO
    assert TestEnum.coerce(TestEnum.BAR) == TestEnum.BAR
    assert TestEnum.coerce('0') == TestEnum.FOO
    assert TestEnum.coerce('1') == TestEnum.BAR
    assert TestEnum.coerce('') is None
    with raises(ValueError):
        TestEnum.coerce('2')
