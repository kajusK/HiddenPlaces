from datetime import datetime
from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import _

from app.database import db
from app.utils import redirect_return
from .forms import LocationForm, VisitForm, DocumentForm, PhotoForm, LinkForm, PhotoEditForm, BookmarkForm, DocumentEditForm
from .models import Location, Visit, Material, Link, Bookmarks
from app.upload.models import Upload
from app.upload.constants import UploadType

blueprint = Blueprint('location', __name__, url_prefix="/location")


@blueprint.route('/<int:id>', methods=['GET', 'POST'])
@blueprint.route('/<int:id>-<string:name>', methods=['GET', 'POST'])
def show(id, name=None):
    location = Location.get_by_id(id)
    if not location:
        return abort(404)
    if name != location.name:
        return redirect(url_for("location.show", id=location.id,
                                name=location.name))

    form = VisitForm()
    bookmark_form = BookmarkForm()
    bookmarks = Bookmarks.get_by_user(current_user)

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
                    subfolder=f"location/{ location.id }/visits",
                    name="Visit photo",
                    type=UploadType.PHOTO,
                    created_by=current_user,
                    object_uuid=visit.uuid,
                )
            db.session.commit()

        flash("Visit logged", "success")
        return redirect(url_for("location.show", id=location.id,
                                name=location.name))

    return render_template("location/location.html", location=location,
                           form=form, bookmark_form=bookmark_form,
                           bookmarks=bookmarks)


@blueprint.route('/search', methods=['POST'])
def search():
    return f"Searching for {request}"


@blueprint.route('/mine')
def owned():
    locations = Location.get_by_owner(current_user)
    return render_template("location/browse.html", locations=locations)


@blueprint.route('/visited')
def visited():
    visits = Visit.get_by_user(current_user)
    locations = []
    for visit in visits:
        if visit.location not in locations:
            locations.append(visit.location)
    return render_template("location/browse.html", locations=locations)


@blueprint.route('/bookmarks/<int:bookmarks_id>')
def bookmarks(bookmarks_id):
    bookmarks = Bookmarks.get_by_id(bookmarks_id)
    if not bookmarks:
        return abort(404)
    return render_template("location/browse.html",
                           locations=bookmarks.locations)


@blueprint.route('/browse')
def browse():
    locations = Location.query.all()
    return render_template("location/browse.html", locations=locations)


@blueprint.route('/add', methods=['GET', 'POST'])
@blueprint.route('/add/<int:parent_id>', methods=['GET', 'POST'])
def add(parent_id=None):
    parent = None
    if parent_id:
        parent = Location.get_by_id(parent_id)

    form = LocationForm()
    if form.validate_on_submit():
        location = Location.create(
            name=form.name.data,
            description=form.description.data,
            about=form.about.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            country=form.country.data,
            type=form.type.data,
            state=form.state.data,
            accessibility=form.accessibility.data,
            length=form.length.data,
            geofond_id=form.geofond_id.data,
            abandoned_year=form.abandoned.data,
            published=int(form.published.data),
            parent_id=parent_id,
            owner=current_user,
        )
        for material in form.materials.data:
            location.materials.append(Material.create(type=material))
        db.session.commit()

        if form.photo.data:
            location.photo = Upload.create(
                file=form.photo.data,
                subfolder=f"location/{ location.id }",
                name="Title photo",
                type=UploadType.PHOTO,
                created_by=current_user
            )
        db.session.commit()

        flash("New location created", "success")
        return redirect(url_for("location.show", id=location.id))

    return render_template("location/edit.html", form=form, parent=parent)


@blueprint.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    location = Location.get_by_id(id)
    if not location:
        return abort(404)

    form = LocationForm()
    if request.method == 'GET':
        form.name.data = location.name
        form.description.data = location.description
        form.about.data = location.about
        form.latitude.data = location.latitude
        form.longitude.data = location.longitude
        form.country.data = location.country
        form.type.data = location.type
        form.state.data = location.state
        form.accessibility.data = location.accessibility
        form.materials.data = [m.type for m in location.materials]
        form.length.data = location.length
        form.geofond_id.data = location.geofond_id
        form.abandoned.data = location.abandoned_year
        form.published.data = '0' if not location.published else '1'

    elif form.validate_on_submit():
        location.name = form.name.data
        location.description = form.description.data
        location.about = form.about.data
        location.latitude = form.latitude.data
        location.longitude = form.longitude.data
        location.country = form.country.data
        location.type = form.type.data
        location.state = form.state.data
        location.accessibility = form.accessibility.data
        location.length = form.length.data
        location.geofond_id = form.geofond_id.data
        location.abandoned_year = form.abandoned.data
        location.published = int(form.published.data)
        location.modified = datetime.utcnow()

        location.materials = []
        for material in form.materials.data:
            location.materials.append(Material.create(type=material))

        if form.photo.data:
            location.photo.delete()

            location.photo = Upload.create(
                file=form.photo.data,
                subfolder=f"location/{ location.id }",
                name=_("Title photo"),
                type=UploadType.PHOTO,
                created_by=current_user,
                object_uuid=location.uuid,
            )
        db.session.commit()

        flash("Location saved", "success")
        return redirect_return()

    return render_template("location/edit.html", form=form, location=location)


@blueprint.route('/visit/edit/<int:visit_id>', methods=['GET', 'POST'])
def visit_edit(visit_id):
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
                    subfolder=f"location/{ visit.location.id }/visits",
                    name="Visit photo",
                    type=UploadType.PHOTO,
                    created_by=current_user,
                    object_uuid=visit.uuid,
                )
        db.session.commit()
        return redirect_return()

    return render_template("location/visit.html", form=form)


@blueprint.route('/visit/delete/<int:visit_id>')
def visit_remove(visit_id):
    visit = Visit.get_by_id(visit_id)
    if not visit:
        return abort(404)

    visit.delete()
    db.session.commit()
    return redirect_return()


@blueprint.route('/photo/add/<int:location_id>', methods=['GET', 'POST'])
def photo_add(location_id):
    location = Location.get_by_id(location_id)
    if not location:
        return abort(404)

    form = PhotoForm()
    if form.validate_on_submit():
        Upload.create(
            file=form.file.data,
            subfolder=f"location/{ location.id }/photos",
            name=form.name.data,
            description=form.description.data,
            created=form.taken_on.data,
            type=UploadType.PHOTO,
            created_by=current_user,
            object_uuid=location.uuid,
        )
        db.session.commit()
        flash("New photo added", "success")
        return redirect_return()

    return render_template("location/photo.html", form=form, location=location)


@blueprint.route('/photo/edit/<int:photo_id>', methods=['GET', 'POST'])
def photo_edit(photo_id):
    photo = Upload.get_by_id(photo_id)
    if not photo:
        return abort(404)

    form = PhotoEditForm()
    if request.method == 'GET':
        form.name.data = photo.name
        form.description.data = photo.description
    elif form.validate_on_submit():
        photo.name = form.name.data
        photo.description = form.description.data
        db.session.commit()
        return redirect_return()

    return render_template("location/photo.html", form=form)


@blueprint.route('/photo/delete/<int:photo_id>')
def photo_remove(photo_id):
    photo = Upload.get_by_id(photo_id)
    if not photo:
        return abort(404)

    photo.delete()
    db.session.commit()
    return redirect_return()


@blueprint.route('/document/add/<int:location_id>', methods=['GET', 'POST'])
def document_add(location_id):
    location = Location.get_by_id(location_id)
    if not location:
        return abort(404)

    form = DocumentForm()
    if form.validate_on_submit():
        Upload.create(
            file=form.file.data,
            subfolder=f"location/{ location.id }/files",
            name=form.name.data,
            description=form.description.data,
            type=form.type.data,
            created_by=current_user,
            object_uuid=location.uuid)

        db.session.commit()
        flash("New document added", "success")
        return redirect_return()

    return render_template("location/document.html", form=form, location=location)


@blueprint.route('/document/remove/<int:document_id>')
def document_remove(document_id):
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
def document_edit(document_id):
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
    return render_template("location/document.html", form=form)


@blueprint.route('/link/add/<int:location_id>', methods=['GET', 'POST'])
def link_add(location_id):
    location = Location.get_by_id(location_id)
    if not location:
        return abort(404)

    form = LinkForm()
    if form.validate_on_submit():
        location.links.append(Link.create(
            url=form.url.data,
            name=form.name.data,
            created_by=current_user))

        db.session.commit()
        flash(_("New document added"), "success")
        return redirect_return()

    return render_template("location/link.html", form=form, location=location)


@blueprint.route('/link/remove/<int:link_id>')
def link_remove(link_id):
    link = Link.get_by_id(link_id)
    if not link:
        return abort(404)

    link.delete()
    db.session.commit()
    return redirect_return()


@blueprint.route('/bookmark/create', methods=['POST'])
@blueprint.route('/bookmark/create/<int:location_id>', methods=['POST'])
def bookmark_create(location_id=None):
    location = None
    if location_id is not None:
        location = Location.get_by_id(location_id)
        if not location:
            return abort(404)

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
        for form, errors in form.errors.items():
            for error in errors:
                flash(_("Adding bookmark failed: %(error)s", error=error),
                      'warning')
    return redirect_return()


@blueprint.route('/bookmark/add/<int:bookmarks_id>/<int:location_id>')
def bookmark_add(bookmarks_id, location_id):
    bookmarks = Bookmarks.get_by_id(bookmarks_id)
    location = Location.get_by_id(location_id)
    if not location or not bookmarks or location in bookmarks.locations:
        return abort(404)

    if location in bookmarks.locations:
        return redirect_return()

    bookmarks.locations.append(location)
    db.session.commit()
    flash(_("Added to bookmark list: %(name)s", name=bookmarks.name),
          'success')
    return redirect_return()


@blueprint.route('/bookmark/remove/<int:bookmarks_id>/<int:location_id>')
def bookmark_remove(bookmarks_id, location_id):
    bookmarks = Bookmarks.get_by_id(bookmarks_id)
    location = Location.get_by_id(location_id)
    if not location or not bookmarks or location not in bookmarks.locations:
        return abort(404)

    bookmarks.locations.remove(location)
    db.session.commit()
    flash(_("Removed from bookmark list: %(name)s", name=bookmarks.name),
          'success')
    return redirect_return()
