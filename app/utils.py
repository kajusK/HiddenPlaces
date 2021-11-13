"""Various helper utilities."""
import re
import urllib.request
import random
import json
import logging
from typing import Optional, Tuple
from enum import Enum
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
    def choices(cls, skip=None):
        """Get list of choices for wtforms (Enum, translation).

        Args:
            skip: List of enum values to be skipped in choices
        """
        data = []
        if skip is None:
            skip = []

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
            return cls(int(item), '')
        except KeyError as e:
            raise ValueError(item) from e

    def __str__(self) -> str:
        """Get string of the item ID."""
        return self.translation


class Pagination:
    """Pagination navigation.

    Attributes:
        current: Current page number
        next: Link to next page or None
        prev: Link to prev page or None
        pages: Dict of page_num: link
        show: Show pagination (more than 1 page)
    """
    # how many page numbers to show
    nav_len = 8
    # how many number show immediately before/after current page
    window_len = 2

    def __init__(self, current, pages, *args, **kwargs):
        """Initializes pagination object

        Call e.g. like Pagination(1, 10, 'some.route', route_arg1=foo).

        Args:
            current: Current page number (starts from 1)
            pages: Amount of pages available
            Rest of the arguments is passed to url_for generator
        """
        self.current = current
        self.prev = None
        self.next = None
        self.pages = {}
        self.show = True

        if pages <= 1:
            self.show = False
            return

        if current == 2:
            self.prev = url_for(*args, **kwargs)
        elif current != 1:
            self.prev = url_for(*args, **kwargs, page=current - 1)

        if current != pages:
            self.next = url_for(*args, **kwargs, page=current + 1)

        if pages <= self.nav_len:
            numbers = list(range(1, pages+1))
        else:
            win_from, win_to = self._get_window(current, pages)

            numbers = list(range(win_from, win_to + 1))
            lower = 1
            upper = pages
            while len(numbers) < self.nav_len:
                if lower < win_from:
                    numbers.append(lower)
                if upper > win_to and len(numbers) < self.nav_len:
                    numbers.append(upper)
                lower += 1
                upper -= 1

        numbers.sort()
        for number in numbers:
            self.pages[number] = url_for(*args, **kwargs, page=number)

    def _get_window(self, current: int, pages: int) -> Tuple[int, int]:
        """Generates window start/end around current page.

        The generated window has self.window_len items and current page
        is centered if possible.

        Args:
            current: Current page number (starts from 1)
            pages: Amount of all pages available
        Returns:
            win_from, win_to: Tuple with window edges
        """
        win_from = current - self.window_len
        win_to = current + self.window_len
        if win_from < 1:
            win_to += 1 + abs(win_from)
            win_from = 1
        if win_to > pages:
            win_from -= win_to - pages
            win_to = pages
            if win_from < 1:  # pylint: disable=consider-using-max-builtin
                win_from = 1
        return win_from, win_to


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


def url_for_return(*args, **kwargs) -> str:
    """Stores current url in session for later return and generates new one."""
    session['return_url'] = request.path
    return url_for(*args, **kwargs)


def url_return() -> str:
    """Generates an url to return to last url_for_return call."""
    return session['return_url'] or url_for('page.index')


def redirect_return():
    """Redirects back from page with url generated by url_return."""
    return redirect(url_return())
