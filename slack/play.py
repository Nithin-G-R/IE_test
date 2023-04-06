import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from slack.db import get_db

play_bp = Blueprint('play', __name__, url_prefix='/play')


@play_bp.route("/", methods=['GET'])
def index():
    return render_template("play/index.html")


@play_bp.route("/music", methods=['GET'])
def music():
    files = [
        {'name': 'Night Piano', 'url': url_for('static', filename='mp3/night_piano.mp3'), 'img': url_for('static', filename='img/piano_icon.jpg')},
        {'name': 'Farm', 'url': url_for('static', filename='mp3/bird.wav'), 'img': url_for('static', filename='img/forest_icon.jpg')},
        {'name': 'Rainfall', 'url': url_for('static', filename='mp3/rainfall.wav'), 'img': url_for('static', filename='img/rainfall_icon.jpg')},
        {'name': 'Calm down', 'url': url_for('static', filename='mp3/calm_down.mp3'),'img': url_for('static', filename='img/calm_down_icon.jpg')},

    ]
    return render_template("play/music.html", files=files)

@play_bp.route("/game", methods=['GET'])
def game():
    return render_template("play/game.html")

@play_bp.route("/podcast", methods=['GET'])
def podcast():
    return render_template("play/podcast.html")
