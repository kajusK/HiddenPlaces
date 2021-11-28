"""Routes for page module.

The page module contains a few generic information pages (about, rules,...)
"""
from typing import Optional
from flask import Blueprint, render_template, request, abort, redirect, \
    url_for, flash
from flask_babel import _
from flask_login import current_user

from app.database import db
from app.utils import redirect_return, url_for_return
from app.decorators import admin
from app.page import email
from app.page.models import Page
from app.page.constants import PageType
from app.page.forms import ContactForm, EditForm

blueprint = Blueprint('page', __name__, url_prefix="/")


def _get_page_type(page: str) -> Optional[PageType]:
    """Gets page type from string

    Args:
        page: Page name (about, rules, support)
    Returns
        None: Not a known page
        PageType: Decoded page type
    """
    ptype = None
    if page == 'about':
        ptype = PageType.ABOUT
    elif page == 'rules':
        ptype = PageType.RULES
    elif page == 'support':
        ptype = PageType.SUPPORT
    return ptype


@blueprint.route('/')
def index():
    """Redirects to default page if no page is specified."""
    return redirect(url_for('location.browse'))


@blueprint.route('/page/edit/<string:page>', methods=['GET', 'POST'])
@admin
def edit(page: str):
    """Renders edit form for editing page content.

    Args:
        page: Page to be edited
    """
    ptype = _get_page_type(page)
    if not ptype:
        abort(404)

    item = Page.get(ptype)
    form = EditForm()
    if request.method == 'GET' and item:
        form.text.data = item.text
    elif form.validate_on_submit():
        if item:
            item.text = form.text.data
        else:
            Page.create(ptype, text=form.text.data)
        db.session.commit()
        return redirect_return()

    return render_template('page/edit.html', form=form, title=str(ptype))


@blueprint.route('/page/<string:page>')
def show(page: str):
    """Renders a text page.

    Args:
        page: Page to be rendered
    """

    ptype = _get_page_type(page)
    if not ptype:
        abort(404)

    query = Page.get(ptype)
    content = _("Nothing added yet") if not query else query.text

    return render_template('page/page.html',
                           edit_url=url_for_return('page.edit', page=page),
                           title=str(ptype), content=content)


@blueprint.route('/page/contact', methods=['GET', 'POST'])
def contact():
    """Renders a contact form."""
    form = ContactForm()
    if form.validate_on_submit():
        email.send_message(current_user, form.subject.data, form.text.data)
        flash(_("Your message was sent"), 'success')
        return redirect(url_for('page.index'))

    return render_template('page/contact.html', form=form)
