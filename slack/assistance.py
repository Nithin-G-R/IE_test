import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from slack.db import get_db

assistance_bp = Blueprint('assistance', __name__, url_prefix='/assistance')


@assistance_bp.route("/", methods=['GET'])
def index():
    return render_template("assistance/index.html")

