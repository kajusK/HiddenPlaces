from flask import Blueprint, render_template, request, flash, abort, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from is_safe_url import is_safe_url

from app.utils import flash_errors
from .models import User
from .forms import LoginForm, RegisterForm

blueprint = Blueprint('user', __name__, url_prefix="/user")


@blueprint.route('/')
@login_required
def profile():
    return render_template("user/profile.html")


@blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        next = request.args.get("next")
        if next and not is_safe_url(next, request.host_url):
            next = None
        return redirect(next or url_for("public.home"))

    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user, remember=form.remember_me.data)
            flash("You are logged in", "success")

            next = request.args.get("next")
            if next and not is_safe_url(next, request.host_url):
                next = None
            return redirect(next or url_for("public.home"))
        else:
            flash_errors(form)
    return render_template("user/login.html", form=form)


@blueprint.route('/logout/')
@login_required
def logout():
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for('user.login'))


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.create(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            user.commit()
            flash("New user registered, you can log in now")
            return redirect(url_for('user.login'))
        else:
            flash_errors(form)
    return render_template('user/register.html', form=form)
