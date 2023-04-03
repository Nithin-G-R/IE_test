import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash

from slack.db import get_db

learn_bp = Blueprint('learn', __name__, url_prefix='/learn')


@learn_bp.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        #   print(request.files)
        return render_template("learn/index.html", file=f)
    else:
        return render_template("learn/index.html")
