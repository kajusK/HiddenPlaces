"""API interface."""
import json
import requests
from requests_html import HTMLSession
from flask import Blueprint, abort

blueprint = Blueprint('api', __name__, url_prefix='/api')


@blueprint.route('/geofond_photos/<int:object_id>')
def geofond_photos(object_id: int):
    """Gets list of geofond mine photos related object

    This cannot be done in browser (javascript) due to same origin policy

    Args:
        object_id: ID of the geofond object
    """
    base_url = 'https://app.geology.cz/dud_foto'
    try:
        session = HTMLSession()
        response = session.get(f'{base_url}/foto_dd.php?id_={object_id}',
                               timeout=3)
    except requests.exceptions.RequestException:
        abort(500)

    images = []

    table = response.html.find('table', first=True)
    if table:
        for link in table.find('a'):
            thumbnail = link.find('img', first=True)
            images.append({
                'url': f"{base_url}/{link.attrs['href']}",
                'thumbnail': thumbnail.attrs['src'],
                'title': thumbnail.attrs['title'],
            })

    return json.dumps({'photos': images})
