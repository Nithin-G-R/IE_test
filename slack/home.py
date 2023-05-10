import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from slack.db import get_db

home_bp = Blueprint('home', __name__, url_prefix='')


@home_bp.route("/", methods=['GET'])
def index():
    return render_template("index.html")


