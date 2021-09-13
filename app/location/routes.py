from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from flask_login import login_required, current_user

from .forms import LocationForm, VisitForm, DocumentForm, PhotoForm
from .models import Location, Visit

blueprint = Blueprint('location', __name__, url_prefix="/location")

@blueprint.route('/<int:id>', methods=['GET', 'POST'])
@blueprint.route('/<int:id>-<string:name>', methods=['GET', 'POST'])
@login_required
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


@blueprint.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    location = Location.get_by_id(id)
    if not location:
        return abort(404)
    #if current_user != location.owner:
    #    return abort(401)

    form = LocationForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            location.name = form.name.data
            location.description = form.description.data
            location.about = form.about.data
            location.latitude = form.latitude.data
            location.longitude = form.longitude.data
            location.commit()
            flash("Location saved", "success")
            return redirect(url_for("location.show",
                            id=location.id,
                            name=location.name))
    else:
        form.name.data = location.name
        form.description.data = location.description
        form.about.data = location.about
        form.latitude.data = location.latitude
        form.longitude.data = location.longitude

    return render_template("location/edit.html", form=form, title=location.name, location=location)


@blueprint.route('/search', methods=['POST'])
@login_required
def search():
    return f"Searching for {request}"


@blueprint.route('/mine')
@login_required
def owned():
    locations = Location.get_by_owner(current_user)
    return render_template("location/browse.html", locations=locations)


@blueprint.route('/visited')
@login_required
def visited():
    locations = Location.get_visited(current_user)
    return render_template("location/browse.html", locations=locations)


@blueprint.route('/bookmarks')
@login_required
def bookmarks():
    locations = Location.get_bookmarked(current_user)
    return render_template("location/browse.html", locations=locations)


@blueprint.route('/browse')
@login_required
def browse():
    locations = Location.query.all()
    return render_template("location/browse.html", locations=locations)


@blueprint.route('/document/<int:location_id>')
@login_required
def add_document(location_id):
    form = DocumentForm(request.form)
    location = Location.get_by_id(location_id)
    return render_template("location/document.html", form=form, location=location)


@blueprint.route('/photo/<int:location_id>')
@login_required
def add_photo(location_id):
    form = PhotoForm(request.form)
    location = Location.get_by_id(location_id)
    return render_template("location/photo.html", form=form, location=location)


@blueprint.route('/add', methods=['GET', 'POST'])
@blueprint.route('/add/<int:parent_id>', methods=['GET', 'POST'])
@login_required
def add(parent_id=None):
    form = LocationForm(request.form)
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
                owner=current_user,
            )
            location.commit()
            flash("New location created", "success")
            return redirect(url_for("location.show", id=location.id))
    return render_template("location/edit.html", form=form, parent=parent)
