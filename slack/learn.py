import functools
import tempfile
import time
import json
import PyPDF2
import os
import requests
import openai
import hashlib
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
        # pdf_data = f.read()
        # print(len(pdf_data))
        hash_value = hashlib.md5(f.read()).hexdigest()
        filename = "{}_{}_{}".format(hash_value, time.time(), f.filename)
        out_file = os.path.join(current_app.static_folder, filename)
        session['pdf'] = filename
        # session['pdf'] = "1682300853936868000_LLaMA- Open and Efficient Foundation Language Models.pdf"
        # print(out_file)
        f.seek(0)
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

def get_answer(question, passage):
    openai.api_key = os.environ["CHAT_API"]

    prompt = "Provide shortest answer to the question based on passage:\n\nQuestion: {}\nPassage: {}".format(question,
                                                                                                             passage)
    model = "text-davinci-002"
    temperature = 0.5
    max_tokens = 50

    # Generate the answer using the OpenAI APIj
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

def generate_summary(passage):
    openai.api_key = os.environ["CHAT_API"]
    prompt = "Provide shortest summary to the passage:\nPassage: {}".format(passage)
    model = "text-davinci-002"
    temperature = 0.5
    max_tokens = 100

    # Generate the answer using the OpenAI API
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )

    # Extract the answer from the OpenAI API response
    summary = response.choices[0].text.strip()
    print(response)
    return summary

@learn_bp.route('/summarizepage', methods=['GET', 'POST'])
def summarize_page():
    page = int(request.args.get('page'))
    try:
        summary = generate_summary(extract_text(session["pdf"])[page - 1])
    except:
        summary = "Server error. Please contact admin for further assistance."

    return jsonify({'summary': summary})

@learn_bp.route('/summarizechapter', methods=['GET'])
def summarize_chapter():
    texts = extract_text(session["pdf"])
    summarized = ""
    try:
        for page in range(len(texts)):
            if page <= 2:
                summarized += (" " + generate_summary(texts[page]))
    except:
        summarized = "Server error. Please contact admin for further assistance."

    chapter_summary = summarized if len(texts) == 1 else generate_summary(summarized)

    return jsonify({'summary': chapter_summary})

@learn_bp.route("/ask", methods=["POST"])
def ask():
    body = request.get_json();
    question = body.get('question')
    if len(question.split()) <= 2:
        answer = "Please ask a question with atleast 3 words."
    else:
        try:
            passage = extract_text(session["pdf"])[current_page - 1]
            answer = get_answer(question=question, passage=passage)
        except:
            answer = "Server error. Please contact admin for further assistance."
    resp = {
        "answer": f"{answer}"
    }
    return jsonify(resp)
