import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from slack.db import get_db

Information_bp = Blueprint('Information', __name__, url_prefix='/Information')


@Information_bp.route("/", methods=['GET'])
def index():
    return render_template("Information/index.html")

@Information_bp.route("/services", methods=['GET'])
def services():
    return render_template("Information/services.html")
