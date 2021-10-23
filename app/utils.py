"""Various helper utilities."""
import re
import urllib.request
import random
import json
import logging
from enum import Enum
from typing import Optional
from urllib.error import URLError
from flask import request, redirect, session, url_for


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
        degrees, minutes, seconds, direction = result.groups(default=0)

        value = float(degrees) + float(minutes)/60 + float(seconds)/3600
        if direction in ('S', 'W'):
            value = -value
        is_latitude = direction in ('N', 'S')
        return cls(value, is_latitude)

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


class OrderedEnum(Enum):
    """Implements Enum that allows comparsion of its elements together."""
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class StringEnum(OrderedEnum):
    """Enum for strings with translations.

    Define items like:
    FOO = 0, _("Translated string")
    """
    def __new__(cls, value, translation):
        """Custom object creation.

        Args:
            value: Numeric value of the item
            translation: Translation string for the item
        """
        obj = object.__new__(cls)
        obj._value_ = value
        obj.translation = translation
        return obj

    @classmethod
    def choices(cls, skip=[]):
        """Get list of choices for wtforms (Enum, translation).

        Args:
            skip: List of enum values to be skipped in choices
        """
        data = []
        for item in cls:
            if item in skip:
                continue
            data.append((item.value, item.translation))
        return data

    @classmethod
    def coerce(cls, item):
        """Coerce method for wtforms.

        Args:
            item: Either class item or name to be coerced or '' for None
        Return:
            Enum item
        Raises:
            ValueError: item not corresponding to any item of this enum
        """
        if isinstance(item, str) and item == '':
            return None

        if isinstance(item, cls):
            return item
        try:
            return cls(int(item))
        except KeyError:
            raise ValueError(item)

    def __str__(self) -> str:
        """Get string of the item ID."""
        return self.translation


def get_visitor_ip() -> Optional[str]:
    """Gets visitors IP address

    Takes visitors behind a reverse proxy into account
    Returns:
        IP address string or None if not known
    """
    if 'X-Forwarded-For' in request.headers:
        header = request.headers.getlist("X-Forwarded-For")[0]
        return header.rpartition(' ')[-1]
    return request.remote_addr or None


def random_string(length: int = 10) -> str:
    """Generates a random string (e.g. for password)

    Args:
        length: length of the string
    """
    characters = list(map(chr, range(ord('a'), ord('z')+1)))
    characters += list(map(chr, range(ord('A'), ord('Z')+1)))
    characters += list(map(str, range(0, 10)))
    characters += list("!@#$%^&*()[],./")

    output = ""
    for _ in range(length):
        output += random.choice(characters)
    return output


def redirect_return():
    """Redirects from page with url generated by url_return."""
    return redirect(session.get('return_url') or url_for('user.login'))
