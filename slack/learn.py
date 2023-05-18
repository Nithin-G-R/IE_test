import functools
import tempfile
import time
import json
import PyPDF2
import os
import requests
import openai
import hashlib
import threading
from functools import wraps
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, jsonify
)
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
from slack.db import get_db

learn_bp = Blueprint('learn', __name__, url_prefix='/learn')

global current_page
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
        if 'pdf' in session.keys():
            texts = extract_text(session['pdf'])
            max_length = len(texts)
        else:
            texts = ['Please upload a correct file to start.']
            max_length = 1
        return render_template("learn/index.html", texts=texts, page=current_page,max_length=max_length)
    else:
        if 'pdf' in session.keys():
            texts = extract_text(session['pdf'])
            max_length = len(texts)
        else:
            texts = ['Please upload a correct file to start.']
            max_length = 1
        return render_template("learn/index.html", texts=texts, page=current_page,max_length=max_length)


@learn_bp.route("/chat", methods=["GET", "POST"])
def chat():
    # global texts
    if request.method == 'POST' and 'page' in request.form:
        current_page = int(request.form['page'])
        # print(current_page)
    else:
        current_page = 1

    if 'pdf' in session.keys():
        texts = extract_text(session['pdf'])
        max_length = len(texts)
    else:
        texts = ['Please upload a correct file to start.']
        max_length = 1

    return render_template("learn/index.html", texts=texts, page=current_page,max_length=max_length)


def extract_text(filename):
    texts = []
    try:
        with open(f"{current_app.static_folder}/" + filename, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            for page in range(num_pages):
                # Get the page object
                pdf_page = pdf_reader.pages[page]

                # Extract the text from the page
                text = pdf_page.extract_text()
                texts.append(text)
    except:
        texts = ['Please upload a correct file to start.']
    return texts

class TimeoutException(Exception):
    pass

def timeout(timeout_seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Define a function to be executed in the thread
            def thread_func():
                try:
                    result = func(*args, **kwargs)
                    thread_func.result = result
                except Exception as e:
                    thread_func.exception = e

            # Create a thread for the function
            thread = threading.Thread(target=thread_func)

            # Start the thread
            thread.start()

            # Wait for the thread to complete with the specified timeout
            thread.join(timeout_seconds)

            # Check if the thread is still alive (not completed within the timeout)
            if thread.is_alive():
                # Thread is still running, handle the timeout
                thread_func.exception = TimeoutException("Timeout occurred")
                #thread.join()  # Wait for the thread to complete after raising the exception

            # Check if an exception was raised in the thread
            if hasattr(thread_func, 'exception'):
                raise thread_func.exception

            # Thread completed within the timeout, you can get the result if needed
            return thread_func.result

        return wrapper

    return decorator

@timeout(7)
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

@timeout(10)
def generate_summary(passage):
    openai.api_key = os.environ["CHAT_API"]

    prompt = "Provide a short comprehensive summary in less than 100 words to the passage:\nPassage: {}".format(passage)
    model = "text-davinci-002"
    temperature = 0.4
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
    # print(response)
    return summary

@learn_bp.route('/summarizepage', methods=['GET', 'POST'])
def summarize_page():
    page = int(request.args.get('page'))
    try:
        summary = generate_summary(extract_text(session["pdf"])[page - 1])
    except TimeoutException:
        summary = "Sorry, Timed out. Try again in a few seconds."
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
        chapter_summary = summarized if len(texts) == 1 else generate_summary(summarized)
    except TimeoutException:
        chapter_summary = "Sorry, Timed out. Try again in a few seconds."
    except:
        chapter_summary = "Server error. Please contact admin for further assistance."



    return jsonify({'summary': chapter_summary})

@learn_bp.route("/ask", methods=["GET", "POST"])
def ask():
    current_page_ask = int(request.args.get('page'))
    # print(current_page_ask)
    body = request.get_json();
    question = body.get('question')
    if len(question.split()) <= 2:
        answer = "Please ask a question with atleast 3 words."
    else:
        try:
            passage = extract_text(session["pdf"])[current_page_ask - 1]
            answer = get_answer(question=question, passage=passage)
        except TimeoutException as e:
            answer = "Sorry, Timed out. Try again in a few seconds"
        except:
            answer = "Server error. Please contact admin for further assistance."
    resp = {
        "answer": f"{answer}"
    }
    return jsonify(resp)
