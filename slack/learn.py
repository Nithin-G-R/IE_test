import functools
import tempfile
import time
import json
import PyPDF2
import os
import requests
import openai

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, jsonify
)
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
from slack.db import get_db

learn_bp = Blueprint('learn', __name__, url_prefix='/learn')

current_page = 1


@learn_bp.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        f = request.files['file']
        print(f.filename)
        filename = "{}_{}".format(time.time(), f.filename)
        out_file = os.path.join(current_app.static_folder, filename)
        session['pdf'] = filename

        f.save(out_file)
        return render_template("learn/index.html")
    else:
        return render_template("learn/index.html")


@learn_bp.route("/chat", methods=["GET", "POST"])
def chat():
    # global texts
    if request.method == 'POST' and 'page' in request.form:
        current_page = int(request.form['page'])
    else:
        current_page = 1
    return render_template("learn/chat.html", texts=extract_text(session['pdf']), page=current_page,
                           max_length=len(extract_text(session['pdf'])))


def extract_text(filename):
    texts = []
    with open(f"{current_app.static_folder}/" + filename, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        for page in range(num_pages):
            # Get the page object
            pdf_page = pdf_reader.pages[page]

            # Extract the text from the page
            text = pdf_page.extract_text()
            texts.append(text)
    return texts


# @learn_bp.route('/pdf_page', methods=['POST'])
# def pdf_page():
#     global current_page
#     current_page = int(request.form['page'])
#     return render_template('learn/chat.html', page=current_page, texts = texts, max_length = len(texts))

def get_answer(question, passage):
    openai.api_key = os.environ["CHAT_API"]
    prompt = "Provide shortest answer to the question based on passage:\n\nQuestion: {}\nPassage: {}".format(question,
                                                                                                             passage)
    model = "text-davinci-002"
    temperature = 0.5
    max_tokens = 50

    # Generate the answer using the OpenAI API
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )

    # Extract the answer from the OpenAI API response
    answer = response.choices[0].text.strip()
    print(response)
    return answer


# def get_answer(context):
#
#     result = model(
#         context,
#         min_length=8,
#         max_length=256,
#         no_repeat_ngram_size=3,
#         encoder_no_repeat_ngram_size=3,
#         repetition_penalty=3.5,
#         num_beams=4,
#         do_sample=False,
#         early_stopping=True,
#     )
#     answer = result[0]['summary_text']
#     return answer


@learn_bp.route("/ask", methods=["POST"])
def ask():
    body = request.get_json();
    question = body.get('question')
    if len(question.split()) <= 2:
        answer = "Please ask a valid quesition."
    else:
        passage = extract_text(session["pdf"])[current_page - 1]
        answer = get_answer(question=question, passage=passage)
    resp = {
        "answer": f"{answer}"
    }
    return jsonify(resp)
