"""Routes for location module."""
from datetime import datetime
from flask import Blueprint, render_template, request, abort, redirect, \
    url_for, flash
from flask_login import current_user
from flask_babel import _

from app.database import db
from app.decorators import moderator
from app.utils.utils import redirect_return
from app.category.forms import CategoryForm
from app.category.models import Category
from app.upload.models import Upload
from app.upload.constants import UploadType
from app.admin import events
from app.admin.models import EventLog


blueprint = Blueprint('category', __name__, url_prefix='/category')


@blueprint.route('/<int:category_id>')
def show(category_id: int):
    """Renders category record.

    Args:
        id: ID of the category
        name: Category name string (for user readable urls)
    """
    category = Category.get_by_id(category_id)
    if not category:
        abort(404)
    return render_template('category/category.html', category=category)


@blueprint.route('/add', methods=['GET', 'POST'])
def add():
    """Renders form for adding new category record."""
    form = CategoryForm()

    if form.validate_on_submit():
        category = Category.create(
            name=form.name.data,
            description=form.description.data,
            about=form.about.data,
            owner=current_user,
        )
        EventLog.log(current_user, events.CreateCategoryEvent(category))
        db.session.commit()

        if form.photo.data:
            category.photo = Upload.create(
                file=form.photo.data,
                subfolder=f'category/{ category.id }',
                name=_("Title photo"),
                type=UploadType.PHOTO,
                created_by=current_user
            )
        db.session.commit()

        flash(_("New category created"), 'success')
        return redirect(url_for('category.show', category_id=category.id))

    return render_template('category/edit.html', form=form)


@blueprint.route('/delete/<int:category_id>')
@moderator
def delete(category_id: int):
    """Deletes the category record

    Args:
        category_id: ID of the category to be deleted
    """
    category = Category.get_by_id(category_id)
    if not category:
        abort(404)

    category.delete()
    EventLog.log(current_user, events.DeleteCategoryEvent(category))
    db.session.commit()
    flash(_("Category was deleted"), 'warning')
    return redirect_return()


@blueprint.route('/edit/<int:category_id>', methods=['GET', 'POST'])
def edit(category_id: int):
    """Renders form for editing existing category record

    Args:
        category_id: ID of the location
    """
    category = Category.get_by_id(category_id)
    if not category:
        return abort(404)

    form = CategoryForm()
    if request.method == 'GET':
        form.name.data = category.name
        form.description.data = category.description
        form.about.data = category.about
    elif form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.about = form.about.data
        category.modified = datetime.utcnow()

        if form.photo.data:
            if not category.photo:
                category.photo = Upload.create(
                    file=form.photo.data,
                    subfolder=f'category/{ category.id }',
                    name=_("Title photo"),
                    type=UploadType.PHOTO,
                    created_by=current_user,
                )
            else:
                category.photo.replace(form.photo.data)
        EventLog.log(current_user, events.ModifyCategoryEvent(category))
        db.session.commit()

        flash(_("Category saved"), 'success')
        return redirect_return()

    return render_template('category/edit.html', form=form,
                           category=category)
