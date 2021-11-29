"""Routes for message module."""
from flask import Blueprint, render_template, request, flash, abort,\
    redirect, url_for
from flask import current_app as app
from flask_login import current_user
from flask_babel import _

from app.database import db
from app.utils import redirect_return, Pagination
from app.user.models import User
from app.message.forms import WriteForm, ReplyForm
from app.message.models import Message, Thread

blueprint = Blueprint('message', __name__, url_prefix="/message")


@blueprint.route('/')
@blueprint.route('/<int:page>')
def browse(page: int = 1):
    """Browse message threads."""
    query = Thread.get(current_user).paginate(
        page, app.config['ITEMS_PER_PAGE'], True)
    pagination = Pagination(page, query.pages, 'message.browse')
    return render_template('message/browse.html', threads=query.items,
                           pagination=pagination)


@blueprint.route('/write/<int:user_id>', methods=['GET', 'POST'])
def write(user_id: int):
    """Create a new message thread.

    Args:
        user_id: ID of the user to send message to
    """
    user = User.get_by_id(user_id)
    if not user:
        abort(404)

    form = WriteForm()
    if form.validate_on_submit():
        thread = Thread.create(
            subject=form.subject.data,
            sender=current_user,
            recipient=user
        )
        Message.create(
            message=form.message.data,
            user=current_user,
            thread=thread,
        )
        db.session.commit()
        flash(_("Message sent"), 'success')
        return redirect_return()
    return render_template('message/write.html', form=form, user=user)


@blueprint.route('/show/<int:thread_id>', methods=['GET', 'POST'])
def show(thread_id: int):
    """Reply to received message.

    Args:
        thread_id: ID of the message thread
    """
    thread = Thread.get_by_id(thread_id)
    if not thread:
        abort(404)
    if current_user not in (thread.sender, thread.recipient):
        abort(403)

    form = ReplyForm()
    if request.method == 'GET':
        thread.mark_seen(current_user)
        db.session.commit()
    elif form.validate_on_submit():
        Message.create(
            message=form.message.data,
            user=current_user,
            thread=thread,
        )
        db.session.commit()
        return redirect(url_for('message.show', thread_id=thread_id))
    return render_template('message/show.html', form=form, thread=thread)
