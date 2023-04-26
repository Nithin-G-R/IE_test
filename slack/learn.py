import functools
import tempfile
import time
import json
import PyPDF2
import requests
import tensorflow as tf
from transformers import AutoTokenizer, TFMobileBertForQuestionAnswering


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, jsonify
)
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
from slack.db import get_db


learn_bp = Blueprint('learn', __name__, url_prefix='/learn')

global current_page, texts
current_page = 1
texts = []

# Load the tokenizer and model from the saved directory
tokenizer = AutoTokenizer.from_pretrained("models/tfmobilebert")
model = TFMobileBertForQuestionAnswering.from_pretrained("models/tfmobilebert")

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
    global texts
    filename = session['pdf']
    texts = extract_text(filename)
    #filename = "1682300853936868000_LLaMA- Open and Efficient Foundation Language Models.pdf"
    return render_template("learn/chat.html", texts = texts, page = current_page, max_length = len(texts))

def extract_text(filename):
    global texts
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

@learn_bp.route('/pdf_page', methods=['POST'])
def pdf_page():
    global current_page
    current_page = int(request.form['page'])
    return render_template('learn/chat.html', page=current_page, texts = texts)


def get_answer(question, context):
    inputs = tokenizer(question, context, max_length=512, truncation=True, padding='max_length', return_tensors="tf")
    outputs = model(**inputs)

    answer_start_index = int(tf.math.argmax(outputs.start_logits, axis=-1)[0])
    answer_end_index = int(tf.math.argmax(outputs.end_logits, axis=-1)[0])

    predict_answer_tokens = inputs.input_ids[0, answer_start_index: answer_end_index + 1]
    answer = tokenizer.decode(predict_answer_tokens)

    return answer



@learn_bp.route("/ask", methods=["POST"])
def ask():
    body = request.get_json();
    question = body.get('question')
    context = texts[current_page - 1]
    answer = get_answer(question = question, context = context)
    resp = {
        "answer": f"{answer}"
    }
    return jsonify(resp)
    
