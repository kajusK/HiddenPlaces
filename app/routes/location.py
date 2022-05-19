"""Routes for locations."""
import json
from typing import Optional
from datetime import datetime
from flask import Blueprint, render_template, request, abort, redirect, \
    url_for, flash
from flask import current_app as app
from flask_login import current_user
from flask_babel import _

from app.database import db
from app.decorators import moderator
from app.utils.pagination import Pagination
from app.utils.utils import redirect_return, Url
from app.models.location import Location, Visit, Link, Bookmarks, POI,\
    LocationType
from app.forms.location import VisitForm, LinkForm,\
    BookmarkForm, POIForm
from app.models.upload import Upload, UploadType
from app.models import event
from app.models.event import EventLog
from app.models.user import User
from app.routes.locations import LocationUtil
from app.forms.locations.underground import UndergroundForm
from app.routes.locations.underground import UndergroundUtil
from app.forms.locations.urbex import UrbexForm
from app.routes.locations.urbex import UrbexUtil
from app.forms.locations.hiking import HikingForm
from app.routes.locations.hiking import HikingUtil


blueprint = Blueprint('location', __name__, url_prefix='/location')


def _get_loc_type(type_string: Optional[str]) -> LocationType:
    """Converts string to location type

    Args:
        type_string: String to be converted
    Returns:
        Converted location type or aborts with 404 if not found
    """
    if type_string is None:
        return LocationType.ALL
    if type_string == "underground":
        return LocationType.UNDERGROUND
    if type_string == "urbex":
        return LocationType.URBEX
    if type_string == "hiking":
        return LocationType.HIKING
    abort(404)
    return LocationType.ALL


@blueprint.route('/<int:location_id>', methods=['GET', 'POST'])
def show(location_id: int):
    """Renders location record.

    Args:
        id: ID of the location
        name: Location name string (for user readable urls)
    """
    location = Location.get_by_id(location_id)
    if not location:
        abort(404)

    form = VisitForm()
    bookmark_form = BookmarkForm()

    if form.validate_on_submit():
        visit = Visit.create(
            comment=form.comment.data,
            visited_on=form.date.data,
            location=location,
            user_id=current_user.id)
        EventLog.log(current_user, event.AddVisitEvent(visit))
        db.session.commit()

        if form.photos.data:
            for photo in form.photos.data:
                Upload.create(
                    file=photo,
                    subfolder=f'location/{ location.id }/visits',
                    name=_("Visit photo"),
                    type=UploadType.PHOTO,
                    created_by=current_user,
                    object_uuid=visit.uuid,
                )
            db.session.commit()

        flash(_("Your visit was saved"), 'success')
        return redirect(url_for('location.show', location_id=location.id))

    return render_template('location/location.html', location=location,
                           form=form, bookmark_form=bookmark_form)


@blueprint.route('/add/<string:type_str>', methods=['GET', 'POST'])
def add(type_str: str):
    """Renders form for adding new location record

    Args:
        type_str: Type of the location
    """
    loc_type = _get_loc_type(type_str)
    util: LocationUtil
    if loc_type == LocationType.UNDERGROUND:
        form = UndergroundForm()
        util = UndergroundUtil()
    elif loc_type == LocationType.URBEX:
        form = UrbexForm()
        util = UrbexUtil()
    elif loc_type == LocationType.HIKING:
        form = HikingForm()
        util = HikingUtil()
    else:
        abort(404)

    if form.validate_on_submit():
        location = Location.create(
            name=form.name.data,
            description=form.description.data,
            about=form.about.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            categories=form.categories.data,
            country=form.country.data,
            published=int(form.published.data),
            owner=current_user,
        )
        util.create(location, form)
        EventLog.log(current_user, event.CreateLocationEvent(location))
        db.session.commit()

        if form.photo.data:
            location.photo = Upload.create(
                file=form.photo.data,
                subfolder=f'location/{ location.id }',
                name=_("Title photo"),
                type=UploadType.PHOTO,
                created_by=current_user
            )
        db.session.commit()

        flash(_("New location created"), 'success')
        return redirect(url_for('location.show', location_id=location.id))

    return render_template('location/edit.html', form=form)


@blueprint.route('/delete/<int:location_id>')
@moderator
def delete(location_id: int):
    """Deletes the location record

    Args:
        location_id: ID of the location to be deleted
    """
    location = Location.get_by_id(location_id)
    if not location:
        abort(404)

    location.delete()
    EventLog.log(current_user, event.DeleteLocationEvent(location))
    db.session.commit()
    flash(_("Location was deleted"), 'warning')
    return redirect_return()


@blueprint.route('/edit/<int:location_id>', methods=['GET', 'POST'])
def edit(location_id: int):
    """Renders form for editing existing location record

    Args:
        location_id: ID of the location
    """
    location = Location.get_by_id(location_id)
    if not location:
        return abort(404)

    util: LocationUtil
    if location.underground_id is not None:
        form = UndergroundForm()
        util = UndergroundUtil()
    elif location.urbex_id is not None:
        form = UrbexForm()
        util = UrbexUtil()
    elif location.hiking_id is not None:
        form = HikingForm()
        util = HikingUtil()
    else:
        abort(404)

    if request.method == 'GET':
        form.name.data = location.name
        form.description.data = location.description
        form.about.data = location.about
        form.latitude.data = location.latitude
        form.longitude.data = location.longitude
        form.categories.data = location.categories.all()
        form.country.data = location.country
        form.published.data = '0' if not location.published else '1'
        util.load(location, form)
    elif form.validate_on_submit():
        location.name = form.name.data
        location.description = form.description.data
        location.about = form.about.data
        location.latitude = form.latitude.data
        location.longitude = form.longitude.data
        location.categories = form.categories.data
        location.country = form.country.data
        location.published = int(form.published.data)
        location.modified = datetime.utcnow()
        util.edit(location, form)

        if form.photo.data:
            if not location.photo:
                location.photo = Upload.create(
                    file=form.photo.data,
                    subfolder=f'location/{ location.id }',
                    name=_("Title photo"),
                    type=UploadType.PHOTO,
                    created_by=current_user,
                )
            else:
                location.photo.replace(form.photo.data)
        EventLog.log(current_user, event.ModifyLocationEvent(location))
        db.session.commit()

        flash(_("Location saved"), 'success')
        return redirect_return()

    return render_template('location/edit.html', form=form, location=location)


@blueprint.route('/search', methods=['POST'])
@blueprint.route('/search/<string:string>')
@blueprint.route('/search/<string:string>/<int:page>')
def search(string: str = None, page: int = 1):
    """Renders result of search in location names.

    Args:
        string: Search string
        page: Page number for results pagination
    """
    if request.method == 'POST':
        string = request.form.get('search')

    query = Location.search(string).paginate(
        page, app.config['LOCATIONS_PER_PAGE'], True)
    pagination = Pagination(page, query.pages, 'location.search',
                            string=string)

    return render_template('location/browse.html', locations=query.items,
                           pagination=pagination)


@blueprint.route('/mine/<string:type_str>')
@blueprint.route('/mine/<string:type_str>/<int:page>')
def owned(type_str: str, page: int = 1):
    """Renders locations owned by current user.

    Args:
        type_str: Type of the location
        page: Page number for results pagination
    """
    loc_type = _get_loc_type(type_str)
    query = Location.get_by_owner(loc_type, current_user).paginate(
        page, app.config['LOCATIONS_PER_PAGE'], True)
    pagination = Pagination(page, query.pages, 'location.owned',
                            type_str=type_str)

    return render_template('location/browse.html', locations=query.items,
                           pagination=pagination)


@blueprint.route('/user/<int:user_id>')
@blueprint.route('/user/<int:user_id>/<int:page>')
def by_user(user_id: int, page: int = 1):
    """Renders locations owned by given user.

    Args:
        user_id: ID of the user
        page: Page number for results pagination
    """
    user = User.get_by_id(user_id)
    if not user:
        abort(404)

    query = Location.get_by_owner(LocationType.ALL, user)
    query = Location.filter_private(query, current_user).paginate(
        page, app.config['LOCATIONS_PER_PAGE'], True)
    pagination = Pagination(page, query.pages, 'location.by_user',
                            user_id=user_id)

    return render_template('location/browse.html', locations=query.items,
                           pagination=pagination)


@blueprint.route('/visited/<string:type_str>')
@blueprint.route('/visited/<string:type_str>/<int:page>')
def visited(type_str: str, page: int = 1):
    """Renders locations visited by currentuser.

    Args:
        type_str: Type of the location
        page: Page number for results pagination
    """
    loc_type = _get_loc_type(type_str)
    query = Location.get_unique_visits(loc_type, current_user).paginate(
        page, app.config['LOCATIONS_PER_PAGE'], True)
    pagination = Pagination(page, query.pages, 'location.visited',
                            type_str=type_str)

    return render_template('location/browse.html', locations=query.items,
                           pagination=pagination)


@blueprint.route('/user/visited/<int:user_id>')
@blueprint.route('/user/visited/<int:user_id>/<int:page>')
def visited_by_user(user_id: int, page: int = 1):
    """Renders locations visited by given user.

    Args:
        user_id: ID of the user
        page: Page number for results pagination
    """
    user = User.get_by_id(user_id)
    if not user:
        abort(404)

    query = Location.get_unique_visits(LocationType.ALL, user)
    query = Location.filter_private(query, current_user).paginate(
        page, app.config['LOCATIONS_PER_PAGE'], True)
    pagination = Pagination(page, query.pages, 'location.visited_by_user',
                            user_id=user_id)

    return render_template('location/browse.html', locations=query.items,
                           pagination=pagination)


@blueprint.route('/bookmarks/<string:name>')
@blueprint.route('/bookmarks/<string:name>/<int:page>')
def bookmark_show(name: str, page: int = 1):
    """Renders locations visited by user.

    Args:
        name: Name of the bookmark
        page: Page number for results pagination
    """
    bookmarks = Bookmarks.get_by_name(current_user, name)
    if not bookmarks:
        abort(404)

    query = bookmarks.locations.paginate(
        page, app.config['LOCATIONS_PER_PAGE'], True)
    pagination = Pagination(page, query.pages, 'location.bookmarks',
                            name=name)

    return render_template('location/browse.html', locations=query.items,
                           pagination=pagination)


@blueprint.route('/browse')
@blueprint.route('/browse/<int:page>')
@blueprint.route('/browse/<string:type_str>')
@blueprint.route('/browse/<string:type_str>/<int:page>')
def browse(type_str: Optional[str] = None, page: int = 1):
    """Renders all locations

    Args:
        type: Type of the location
        page: Page number for results pagination
    """
    loc_type = _get_loc_type(type_str)
    query = Location.filter_private(Location.get(loc_type), current_user)
    query = query.paginate(page, app.config['LOCATIONS_PER_PAGE'], True)

    pagination = Pagination(page, query.pages, 'location.browse',
                            type_str=type_str)
    return render_template('location/browse.html', locations=query.items,
                           pagination=pagination)


@blueprint.route('/visit/edit/<int:visit_id>', methods=['GET', 'POST'])
def visit_edit(visit_id: int):
    """Renders form for exiting existing visit record

    Args:
        visit_id: ID of the visit record
    """
    visit = Visit.get_by_id(visit_id)
    if not visit:
        return abort(404)

    form = VisitForm()
    if request.method == 'GET':
        form.comment.data = visit.comment
        form.date.data = visit.visited_on
    elif form.validate_on_submit():
        visit.comment = form.comment.data
        visit.visited_on = form.date.data
        if form.photos.data:
            for photo in form.photos.data:
                Upload.create(
                    file=photo,
                    subfolder=f'location/{ visit.location.id }/visits',
                    name=_("Visit photo"),
                    type=UploadType.PHOTO,
                    created_by=current_user,
                    object_uuid=visit.uuid,
                )
        EventLog.log(current_user, event.ModifyVisitEvent(visit))
        db.session.commit()
        flash(_("Visit was saved"), 'success')
        return redirect_return()

    return render_template('location/visit.html', form=form)


@blueprint.route('/visit/delete/<int:visit_id>')
def visit_remove(visit_id: int):
    """Deletes visit record

    Args:
        visit_id: ID of the visit record
    """
    visit = Visit.get_by_id(visit_id)
    if not visit:
        return abort(404)

    visit.delete()
    EventLog.log(current_user, event.DeleteVisitEvent(visit))
    db.session.commit()
    flash(_("Visit was deleted"), 'success')
    return redirect_return()


@blueprint.route('/link/add/<int:location_id>', methods=['GET', 'POST'])
def link_add(location_id: int):
    """Renders form for adding a new link

    Args:
        location_id: ID of the location the link belongs to
    """
    location = Location.get_by_id(location_id)
    if not location:
        abort(404)

    form = LinkForm()
    if form.validate_on_submit():
        Link.create(
            location_id=location.id,
            url=form.url.data,
            name=form.name.data,
            created_by=current_user)

        db.session.commit()
        flash(_("New link added"), 'success')
        return redirect_return()

    return render_template('location/link.html', form=form, location=location)


@blueprint.route('/link/remove/<int:link_id>')
def link_remove(link_id: int):
    """Removes link record

    Args:
        link_id: ID of the link to be removed
    """
    link = Link.get_by_id(link_id)
    if not link:
        abort(404)

    link.delete()
    db.session.commit()
    return redirect_return()


@blueprint.route('/poi/add/<int:location_id>', methods=['GET', 'POST'])
def poi_add(location_id: int):
    """Renders form for adding a new POI

    Args:
        location_id: ID of the location the POI belongs to
    """
    location = Location.get_by_id(location_id)
    if not location:
        abort(404)

    form = POIForm()
    if form.validate_on_submit():
        POI.create(
            location_id=location.id,
            name=form.name.data,
            description=form.description.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            created_by=current_user)

        db.session.commit()
        flash(_("New POI added"), 'success')
        return redirect_return()

    return render_template('location/poi.html', form=form, location=location)


@blueprint.route('/poi/remove/<int:poi_id>')
def poi_remove(poi_id: int):
    """Removes POI record

    Args:
        poi_id: ID of the POI to be removed
    """
    poi = POI.get_by_id(poi_id)
    if not poi:
        abort(404)

    poi.delete()
    db.session.commit()
    return redirect_return()


@blueprint.route('/bookmark/create', methods=['POST'])
@blueprint.route('/bookmark/create/<int:location_id>', methods=['POST'])
def bookmark_create(location_id: Optional[int] = None):
    """Renders a form to add a new bookmark list.

    Args:
        location_id: Add given location to new list if set
    """
    location = None
    if location_id is not None:
        location = Location.get_by_id(location_id)
        if not location:
            abort(404)

    form = BookmarkForm()
    if form.validate_on_submit():
        Bookmarks.create(
            name=form.name.data,
            user=current_user,
            locations=[location] if location else [],
        )
        db.session.commit()
        flash(_("The bookmark list %(name)s created", name=form.name.data),
              'success')
    else:
        for form, errors in form.errors.items():  # pylint: disable=no-member
            for error in errors:
                flash(_("Adding bookmark list failed: %(error)s", error=error),
                      'warning')
    return redirect_return()


@blueprint.route('/bookmark/add/<int:bookmarks_id>/<int:location_id>')
def bookmark_add(bookmarks_id: int, location_id: int):
    """Adds location to bookmark list.

    Args:
        bookmarks_id: ID of the bookmarks list
        location_id: ID of the location to add to list
    """
    bookmarks = Bookmarks.get_by_id(bookmarks_id)
    location = Location.get_by_id(location_id)
    if not location or not bookmarks or location in bookmarks.locations:
        abort(404)
    if bookmarks.user != current_user:
        abort(403)

    bookmarks.locations.append(location)
    db.session.commit()
    flash(_("Added to bookmark list: %(name)s", name=bookmarks.name),
          'success')
    return redirect_return()


@blueprint.route('/bookmark/remove/<int:bookmarks_id>/<int:location_id>')
def bookmark_remove(bookmarks_id: int, location_id: int):
    """Removes location from bookmark list.

    Args:
        bookmarks_id: ID of the bookmarks list
        location_id: ID of the location to remove from list
    """
    bookmarks = Bookmarks.get_by_id(bookmarks_id)
    location = Location.get_by_id(location_id)
    if not location or not bookmarks or location not in bookmarks.locations:
        abort(404)
    if bookmarks.user != current_user:
        abort(403)

    bookmarks.locations.remove(location)
    db.session.commit()
    flash(_("Removed from bookmark list: %(name)s", name=bookmarks.name),
          'success')
    return redirect_return()


@blueprint.route('/map')
@blueprint.route('/map/<string:type_str>')
def browse_map(type_str: Optional[str] = None):
    """Renders locations in map

    Args:
        type: Type of the location
    """
    return render_template('location/map.html', loc_type=type_str)


@blueprint.route('/api')
@blueprint.route('/api/<string:type_str>')
def api(type_str: Optional[str] = None):
    """Gets locations in json.

    Args:
        type_str: type of the location (urbex, underground,...)
    """
    query = Location.get(_get_loc_type(type_str))
    locations = Location.filter_private(query, current_user).all()
    results = []

    for location in locations:
        if location.photo:
            image_url = Url.get('upload.get', path=location.photo.thumbnail)
        else:
            image_url = Url.get(
                'static', filename='images/location_placeholder.png')

        if location.underground:
            loc_type = location.underground.type
            loc_state = location.underground.state
            loc_accessibility = location.underground.accessibility
        elif location.urbex:
            loc_type = location.urbex.type
            loc_state = location.urbex.state
            loc_accessibility = location.urbex.accessibility
        elif location.hiking:
            loc_type = location.hiking.type
            loc_state = _('Undefined')
            loc_accessibility = _('Undefined')

        results.append({
            'id': location.id,
            'name': location.name,
            'image': str(image_url),
            'description': location.description,
            'latitude': location.latitude.value,
            'longitude': location.longitude.value,
            'type': str(loc_type),
            'state': str(loc_state),
            'accessibility': str(loc_accessibility),
        })

    return json.dumps({'locations': results})
