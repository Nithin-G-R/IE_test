import functools
import tempfile
import time

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
from slack.db import get_db


learn_bp = Blueprint('learn', __name__, url_prefix='/learn')


@learn_bp.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        f = request.files['file']
        print(f.filename)
        # pdf_data = f.read()
        # print(len(pdf_data))
        filename = "{}_{}".format(time.time(), f.filename)
        out_file = os.path.join(current_app.static_folder, filename)
        session['pdf'] = filename
        # print(out_file)
        f.save(out_file)
        return render_template("learn/index.html")
    else:
        return render_template("learn/index.html")
