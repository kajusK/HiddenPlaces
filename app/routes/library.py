"""Routes for library."""
from flask import Blueprint, render_template
from flask import current_app as app

from app.utils.pagination import Pagination
from app.models.upload import Upload, UploadType


blueprint = Blueprint('library', __name__, url_prefix="/library")


@blueprint.route('/')
@blueprint.route('/<int:page>')
def browse(page: int = 1):
    """Browse all books

    Args:
        page: Page for pagination
    """
    query = Upload.get(UploadType.BOOK).paginate(
        page, app.config['ITEMS_PER_PAGE'], True)
    pagination = Pagination(page, query.pages, 'library.browse')
    return render_template('library/browse.html', books=query.items,
                           pagination=pagination)
