"""Geolocation utilities."""
import re
import urllib.request
import logging
import json
from urllib.error import URLError


class GeoIp:
    """ A simple geolocation API.

    All the attributes can be NULL in case of internal IP addres or failed
    remote server communication.

    Attributes:
        valid (bool): Location validity, if False the Location query failed.
        country (str): A country name.
        country_code (str): A code of the country (e.g. CZ for Czech Republic).
        city (str): A city name.
        lat (str): A latitude of the IP location.
        lat (str): A longitude of the IP location.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, ip: str) -> None:
        """Obtains geolocation information from remote server.

        Args:
            ip: IP address to get the location for.
        """
        query = f"https://geolocation-db.com/json/{ip}"
        data = {}
        self.valid = True
        try:
            with urllib.request.urlopen(query) as url:
                data = json.loads(url.read().decode('utf-8'))
        except URLError as ex:
            logging.warning("Failed to obtain GeoIP info: %s", ex)
            self.valid = False
        except json.JSONDecodeError as ex:
            logging.warning("Failed to decode GeoIP response: %s", ex)
            self.valid = False

        self.country = data.get('country_name')
        self.country_code = data.get('country_code')
        self.city = data.get('city')
        self.lat = data.get('latitude')
        self.lon = data.get('longitude')


class LatLon:
    """Geolocation coordinates handling and conversions.

    Attributes:
        value: Decimal degrees value of the latitude/longitude
        is_latitude: True if this instance is latitude
        is_longitude: True if this instance is longitude
    """

    def __init__(self, value: float, is_latitude: bool) -> None:
        """Initializes a LatLon object.

        Args:
            value: decimal degrees value
            is_latitue: True if is latitude record, false otherwise
        Raises:
            ValueError: When string doesn't contain valid data
        """
        self.value = value
        self.is_latitude = is_latitude
        self.is_longitude = not is_latitude
        self._check_bounds()

    @classmethod
    def from_str(cls, data: str):
        """Converts the lat/lon string to numerical value

        Args:
            data: String to be converted (15.1234N, 15°24'15.2"N, 15°24.15'N)
        Raises:
            ValueError: When string doesn't contain valid data
        """
        data = data.strip().replace(' ', '').upper()

        result = re.search(
            r'^([0-9.]+)(?:°([0-9.]+)\'(?:([0-9.]+)")?)?([NSEW])$', data)
        if not result:
            raise ValueError(f"Invalid latlon format: {data}")
        degrees, minutes, seconds, direction = result.groups(default='0')

        value = float(degrees) + float(minutes)/60 + float(seconds)/3600
        if direction in ('S', 'W'):
            value = -value
        is_latitude = direction in ('N', 'S')
        return cls(value, is_latitude)

    def to_decimal_str(self) -> str:
        """Converts the object to decimal string, e.g. 12.123E"""
        if self.is_latitude:
            direction = 'N' if self.value >= 0 else 'S'
        else:
            direction = 'E' if self.value >= 0 else 'W'
        return f'{abs(self.value):.6f}{direction}'

    def _check_bounds(self):
        """Checks bounds of the value according to latitude/longitude. """
        if self.is_latitude and abs(self.value) > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if self.is_longitude and abs(self.value) > 180:
            raise ValueError("Longitude must be between -180 and 180 degrees")

    def __str__(self) -> str:
        """Creates a textual representation of the coordinates. """
        if self.is_latitude:
            direction = 'N' if self.value >= 0 else 'S'
        else:
            direction = 'E' if self.value >= 0 else 'W'

        value = abs(self.value)
        degrees = int(value)
        minutes = int((value - degrees)*60)
        seconds = (value - degrees - minutes/60)*3600

        return f'{degrees}°{minutes}\'{seconds:.1f}" {direction}'
