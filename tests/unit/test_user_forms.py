""" Unit tests for user.forms. """
from unittest.mock import patch, mock_open
from urllib.error import URLError
from flask import request
from werkzeug.datastructures import MultiDict
from app.utils import GeoIp, get_visitor_ip
