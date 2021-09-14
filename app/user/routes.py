from flask import Blueprint, render_template, request, flash, abort, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from is_safe_url import is_safe_url

from .models import User
from .forms import LoginForm, RegisterForm, ChangePasswordForm, EditProfileForm, InviteForm, BanForm
from app.location.models import Location, Visit

blueprint = Blueprint('user', __name__, url_prefix="/user")


@blueprint.route('/')
@blueprint.route('/<int:id>')
@login_required
def profile(id=None):
    user = current_user if not id else User.get_by_id(id)
    locations = Location.get_by_owner(user)
    visits = Visit.get_by_user(user)
    return render_template("user/profile.html", user=user, locations=locations,
                           visits=visits)


@blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        next = request.args.get("next")
        if next and not is_safe_url(next, request.host_url):
            next = None
        return redirect(next or url_for("location.browse"))

    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user, remember=form.remember_me.data)
            flash("You are logged in", "success")

            next = request.args.get("next")
            if next and not is_safe_url(next, request.host_url):
                next = None
            return redirect(next or url_for("location.browse"))
    return render_template("user/login.html", form=form)


@blueprint.route('/logout/')
@login_required
def logout():
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for('user.login'))


@blueprint.route('/reset_password/', methods=['GET', 'POST'])
def reset_password():
    pass


@blueprint.route('/change_password/', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    return render_template('user/password.html', form=form)


@blueprint.route('/edit/')
@login_required
def edit():
    form = EditProfileForm()
    return render_template('user/edit.html', form=form)


@blueprint.route('/ban/')
@login_required
def ban():
    form = BanForm()
    return render_template('user/ban.html', form=form, user=current_user)


@blueprint.route('/role/')
@login_required
def role():
    return render_template('user/role.html')


@blueprint.route('/invite/')
@login_required
def invite():
    form = InviteForm()
    return render_template('user/invite.html', form=form)


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.create(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                password=form.password.data
            )
            user.commit()
            flash("New user registered, you can log in now", "success")
            return redirect(url_for('user.login'))
    return render_template('user/register.html', form=form)
