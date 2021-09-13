from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from flask_login import login_required, current_user

from .forms import ContactForm, EditForm

blueprint = Blueprint('page', __name__, url_prefix="/")


@blueprint.route('/page/edit/<int:id>/')
@login_required
def edit(id):
    form = EditForm()
    return render_template('page/edit.html', form=form)


@blueprint.route('/contact/')
@login_required
def contact():
    form = ContactForm()
    return render_template('page/contact.html', form=form)


@blueprint.route('/support/')
@login_required
def support():
    return render_template('page/page.html', page_edit_url=url_for('page.edit', id=0),
                           page_title="support me!", page_content="# suport me!\nfoo *bar*")


@blueprint.route('/rules/')
@login_required
def rules():
    return render_template('page/page.html', page_edit_url=url_for('page.edit', id=0),
                           page_title="Rules pyčo", page_content="# some random page rules\nfoo *bar*")


@blueprint.route('/about/')
@login_required
def about():
    return render_template('page/page.html', page_edit_url=url_for('page.edit', id=0),
        page_title="About this page", page_content="# some random page about\nfoo *bar*")
