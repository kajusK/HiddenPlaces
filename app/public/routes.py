from flask import Blueprint, render_template
from flask_login import login_required

blueprint = Blueprint('public', __name__)


@blueprint.route('/')
@login_required
def home():
    return render_template("public/home.html")
