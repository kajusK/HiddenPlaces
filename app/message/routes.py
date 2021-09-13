from flask import Blueprint, render_template, request, flash, abort, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from is_safe_url import is_safe_url

from .forms import NewMessageForm, ReplyForm

blueprint = Blueprint('message', __name__, url_prefix="/message")


@blueprint.route('/')
@login_required
def list():
    return render_template('message/list.html')


@blueprint.route('/new/')
@login_required
def new():
    form = NewMessageForm()
    return render_template('message/new.html', form=form)


@blueprint.route('/<int:id>')
@login_required
def show(id):
    class Msg():
        from datetime import datetime
        date = datetime.now()
        user = current_user
        text = "hello you bastard"

    form = ReplyForm()
    messages = [Msg(), Msg(), Msg()]
    return render_template('message/show.html', form=form, msgs=messages)


@blueprint.route('/delete/<int:id>')
@login_required
def delete(id):
    return redirect(url_for("message.list"))
