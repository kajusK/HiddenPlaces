from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from flask_login import login_required, current_user

from app.user.models import User
from app.location.models import Location

blueprint = Blueprint('admin', __name__, url_prefix="/admin")


@blueprint.route('/users')
@login_required
def users():
    users = User.query.all()
    return render_template("admin/users.html", users=users)


@blueprint.route('/locations')
@login_required
def locations():
    locs = Location.query.all()
    return render_template("admin/locations.html", locations=locs)


@blueprint.route('/invitations')
@login_required
def invitations():
    return render_template("admin/invitations.html")


@blueprint.route('/settings')
@login_required
def settings():
    return render_template("admin/settings.html")


@blueprint.route('/logins')
@login_required
def logins():
    return render_template("admin/logins.html")
