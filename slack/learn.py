import functools
import tempfile
import time
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, jsonify
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
        #session['pdf'] = "1682300853936868000_LLaMA- Open and Efficient Foundation Language Models.pdf"
        # print(out_file)
        f.save(out_file)
        return render_template("learn/index.html")
    else:
        return render_template("learn/index.html")


@learn_bp.route("/chat", methods=["GET"])
def chat():
    filename = session['pdf']
    #filename = "1682300853936868000_LLaMA- Open and Efficient Foundation Language Models.pdf"
    return render_template("learn/chat.html")


@learn_bp.route("/ask", methods=["POST"])
def ask():
    body = request.get_json();
    
    resp = {
        "answer": "I don't know your question about {}".format(body.get("question"))
    }
    return jsonify(resp)
    