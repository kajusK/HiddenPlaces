"""Various helper utilities."""
import urllib.request
import random
import json
import logging
from typing import Optional
from urllib.error import URLError
from flask import request


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
