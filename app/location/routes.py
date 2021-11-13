"""Routes for location module."""
from typing import Optional
from datetime import datetime
from flask import Blueprint, render_template, request, abort, redirect, \
    url_for, flash
from flask import current_app as app
from flask_login import current_user
from flask_babel import _

from app.database import db
from app.decorators import moderator
from app.utils import redirect_return, Pagination
from app.location.forms import VisitForm, DocumentForm, PhotoForm, LinkForm, \
     PhotoEditForm, BookmarkForm, DocumentEditForm
from app.location.models import Location, Visit, Link, Bookmarks
from app.location.constants import LocationType
from app.location.underground.forms import UndergroundForm
from app.location.underground.utils import UndergroundUtil
from app.location.urbex.forms import UrbexForm
from app.location.urbex.utils import UrbexUtil
from app.upload.models import Upload
from app.upload.constants import UploadType


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
    abort(404)
    return LocationType.ALL


@blueprint.route('/<int:location_id>', methods=['GET', 'POST'])
@blueprint.route('/<int:location_id>-<string:name>', methods=['GET', 'POST'])
def show(location_id: int, name: str = None):
    """Renders location record.

    Args:
        id: ID of the location
        name: Location name string (for user readable urls)
    """
    location = Location.get_by_id(location_id)
    if not location:
        abort(404)
    if name != location.name:
        return redirect(url_for('location.show', location_id=location.id,
                                name=location.name))

    form = VisitForm()
    bookmark_form = BookmarkForm()

    if form.validate_on_submit():
        visit = Visit.create(
            comment=form.comment.data,
            visited_on=form.date.data,
            location=location,
            user_id=current_user.id)
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
        return redirect(url_for('location.show', location_id=location.id,
                                name=location.name))

    return render_template('location/location.html', location=location,
                           form=form, bookmark_form=bookmark_form)


@blueprint.route('/add/<string:type_str>', methods=['GET', 'POST'])
@blueprint.route('/add/<string:type_str>/<int:parent_id>',
                 methods=['GET', 'POST'])
def add(type_str: str, parent_id: Optional[int] = None):
    """Renders form for adding new location record

    Args:
        type_str: Type of the location
        parent_id: ID of the parent location if creating child
    """
    parent = None
    if parent_id:
        parent = Location.get_by_id(parent_id)

    loc_type = _get_loc_type(type_str)
    if loc_type == LocationType.UNDERGROUND:
        form = UndergroundForm()
        util = UndergroundUtil()
    elif loc_type == LocationType.URBEX:
        form = UrbexForm()
        util = UrbexUtil()
    else:
        abort(404)

    if form.validate_on_submit():
        location = Location.create(
            name=form.name.data,
            description=form.description.data,
            about=form.about.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            country=form.country.data,
            published=int(form.published.data),
            parent_id=parent_id,
            owner=current_user,
        )
        util.create(location, form)
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

    return render_template('location/edit.html', form=form, parent=parent)


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

    if location.underground_id is not None:
        form = UndergroundForm()
        util = UndergroundUtil()
    elif location.urbex_id is not None:
        form = UrbexForm()
        util = UrbexUtil()
    else:
        abort(404)

    if request.method == 'GET':
        form.name.data = location.name
        form.description.data = location.description
        form.about.data = location.about
        form.latitude.data = location.latitude
        form.longitude.data = location.longitude
        form.country.data = location.country
        form.published.data = '0' if not location.published else '1'
        util.load(location, form)
    elif form.validate_on_submit():
        location.name = form.name.data
        location.description = form.description.data
        location.about = form.about.data
        location.latitude = form.latitude.data
        location.longitude = form.longitude.data
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
        page, app.config['ITEMS_PER_PAGE'], True)
    pagination = Pagination(page, query.pages, 'location.search',
                            string=string)

    return render_template('location/browse.html', locations=query.items,
                           pagination=pagination)


@blueprint.route('/mine/<string:type_str>')
@blueprint.route('/mine/<string:type_str>/<int:page>')
def owned(type_str: str, page: int = 1):
    """Renders locations owned by user.

    Args:
        type_str: Type of the location
        page: Page number for results pagination
    """
    loc_type = _get_loc_type(type_str)
    query = Location.get_by_owner(loc_type, current_user).paginate(
        page, app.config['ITEMS_PER_PAGE'], True)
    pagination = Pagination(page, query.pages, 'location.owned',
                            type_str=type_str)

    return render_template('location/browse.html', locations=query.items,
                           pagination=pagination)


@blueprint.route('/visited/<string:type_str>')
@blueprint.route('/visited/<string:type_str>/<int:page>')
def visited(type_str: str, page: int = 1):
    """Renders locations visited by user.

    Args:
        type_str: Type of the location
        page: Page number for results pagination
    """
    loc_type = _get_loc_type(type_str)
    query = Location.get_unique_visits(loc_type, current_user).paginate(
        page, app.config['ITEMS_PER_PAGE'], True)
    pagination = Pagination(page, query.pages, 'location.visited',
                            type_str=type_str)

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
        page, app.config['ITEMS_PER_PAGE'], True)
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
    query = Location.get(loc_type).paginate(
        page, app.config['ITEMS_PER_PAGE'], True)
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
    db.session.commit()
    flash(_("Visit was deleted"), 'success')
    return redirect_return()


@blueprint.route('/photo/add/<int:location_id>', methods=['GET', 'POST'])
def photo_add(location_id: int):
    """Renders for for uploading a new photo

    Args:
        location_id: ID of the location to which we are uploading
    """
    location = Location.get_by_id(location_id)
    if not location:
        return abort(404)

    form = PhotoForm()
    if form.validate_on_submit():
        Upload.create(
            file=form.file.data,
            subfolder=f'location/{ location.id }/photos',
            name=form.name.data,
            description=form.description.data,
            created=form.taken_on.data,
            type=UploadType.PHOTO,
            created_by=current_user,
            object_uuid=location.uuid,
        )
        db.session.commit()
        flash(_("New photo added"), 'success')
        return redirect_return()

    return render_template('location/photo.html', form=form, location=location)


@blueprint.route('/photo/edit/<int:photo_id>', methods=['GET', 'POST'])
def photo_edit(photo_id: int):
    """Renders for for editing existing photo

    Args:
        photo_id: ID of the photo to be edited
    """
    photo = Upload.get_by_id(photo_id)
    if not photo:
        abort(404)

    form = PhotoEditForm()
    if request.method == 'GET':
        form.name.data = photo.name
        form.description.data = photo.description
    elif form.validate_on_submit():
        photo.name = form.name.data
        photo.description = form.description.data
        db.session.commit()
        return redirect_return()

    return render_template('location/photo.html', form=form)


@blueprint.route('/photo/delete/<int:photo_id>')
def photo_remove(photo_id: int):
    """Deletes photo record

    Args:
        photo_id: ID of the photo to be deleted
    """
    photo = Upload.get_by_id(photo_id)
    if not photo:
        abort(404)

    photo.delete()
    db.session.commit()
    return redirect_return()


@blueprint.route('/document/add/<int:location_id>', methods=['GET', 'POST'])
def document_add(location_id: int):
    """Renders form for adding a new document

    Args:
        location_id: ID of the location the document belongs to
    """
    location = Location.get_by_id(location_id)
    if not location:
        abort(404)

    form = DocumentForm()
    if form.validate_on_submit():
        Upload.create(
            file=form.file.data,
            subfolder=f'location/{ location.id }/files',
            name=form.name.data,
            description=form.description.data,
            type=form.type.data,
            created_by=current_user,
            object_uuid=location.uuid)

        db.session.commit()
        flash(_("New document added"), 'success')
        return redirect_return()

    return render_template('location/document.html', form=form,
                           location=location)


@blueprint.route('/document/remove/<int:document_id>')
def document_remove(document_id: int):
    """Removes document entry.

    Args:
        document_id: ID of the document to be removed
    """
    document = Upload.get_by_id(document_id)
    if not document:
        return abort(404)

    document.delete()
    db.session.commit()
    return redirect_return()


@blueprint.route('/document/edit/<int:document_id>', methods=['GET', 'POST'])
def document_edit(document_id: int):
    """Edits document entry.

    Args:
        document_id: ID of the document to be edited
    """
    document = Upload.get_by_id(document_id)
    if not document:
        return abort(404)

    form = DocumentEditForm()
    if request.method == 'GET':
        form.name.data = document.name
        form.description.data = document.description
        form.type.data = document.type

    elif form.validate_on_submit():
        document.name = form.name.data
        document.description = form.description.data
        document.type = form.type.data
        if form.file.data:
            document.replace(form.file.data)
        db.session.commit()
        return redirect_return()

    return render_template('location/document.html', form=form)


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
