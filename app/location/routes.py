from datetime import datetime
from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import _

from app.database import db
from .forms import LocationForm, VisitForm, DocumentForm, PhotoForm
from .models import Location, Visit, Material
from app.upload.models import Upload
from app.upload.constants import UploadType

blueprint = Blueprint('location', __name__, url_prefix="/location")

@blueprint.route('/<int:id>', methods=['GET', 'POST'])
@blueprint.route('/<int:id>-<string:name>', methods=['GET', 'POST'])
def show(id, name=None):
    location = Location.get_by_id(id)
    if not location:
        return abort(404)
    # TODO deny access to users that cannot view this page
    if name != location.name:
        return redirect(url_for("location.show", id=location.id,
                                name=location.name))

    is_editable = location.owner == current_user

    form = VisitForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            location.visits.append(Visit(
                comment=form.comment.data,
                visited_on=form.date.data,
                user=current_user))
            location.visits[-1].commit()
            flash("Visit logged", "success")
            return redirect(url_for("location.show",
                                    id=location.id,
                                    name=location.name))
    return render_template("location/location.html",
                           location=location,
                           editable=is_editable,
                           form=form,
                           title=location.name)




@blueprint.route('/search', methods=['POST'])
def search():
    return f"Searching for {request}"


@blueprint.route('/mine')
def owned():
    locations = Location.get_by_owner(current_user)
    return render_template("location/browse.html", locations=locations)


@blueprint.route('/visited')
def visited():
    locations = Location.get_visited(current_user)
    return render_template("location/browse.html", locations=locations)


@blueprint.route('/bookmarks')
def bookmarks():
    locations = Location.get_bookmarked(current_user)
    return render_template("location/browse.html", locations=locations)


@blueprint.route('/browse')
def browse():
    locations = Location.query.all()
    return render_template("location/browse.html", locations=locations)


@blueprint.route('/document/<int:location_id>')
def add_document(location_id):
    form = DocumentForm()
    location = Location.get_by_id(location_id)
    return render_template("location/document.html", form=form, location=location)


@blueprint.route('/photo/<int:location_id>')
def add_photo(location_id):
    form = PhotoForm()
    location = Location.get_by_id(location_id)
    return render_template("location/photo.html", form=form, location=location)


@blueprint.route('/add', methods=['GET', 'POST'])
@blueprint.route('/add/<int:parent_id>', methods=['GET', 'POST'])
def add(parent_id=None):
    form = LocationForm()
    parent = None
    if parent_id:
        parent = Location.get_by_id(parent_id)

    if request.method == 'POST':
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
                    created_by=current_user,
                    object_uuid=location.uploads_uuid,
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
                object_uuid=location.uploads_uuid,
            )
        db.session.commit()

        flash("Location saved", "success")
        return redirect(url_for("location.show", id=location.id,
                                name=location.name))

    return render_template("location/edit.html", form=form, location=location)
