from flask import (
    Flask,
    render_template,
    request,
    flash,
    get_flashed_messages,
    url_for,
    redirect
)
from dotenv import load_dotenv
import os
from .url import validate, normalize
from . import db_worker
from datetime import date
from .response import get_response
from .html_parser import get_tags_content_from_response


load_dotenv()  # take environment variables from .env.

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.route("/")
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.post("/urls")
def add_url():
    url = request.form.get('url')
    errors = validate(url)
    if errors:
        flash(errors, 'error')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            input_url=url,
            messages=messages
        ), 422

    normalized_url = normalize(url)
    connection = db_worker.connection()
    url = db_worker.get_url_by_name(connection, normalized_url)
    if url:
        id = url[0]
        flash("Страница уже существует", 'info')
    else:
        connection = db_worker.connection()
        id = db_worker.add_url_to_db_urls(connection, normalized_url)
        flash("Страница успешно добавлена", 'success')

    return redirect(url_for('show_url', id=id), 302)


@app.get("/urls/<int:id>")
def show_url(id):
    connection = db_worker.connection()
    url = db_worker.get_url_by_id(connection, id)
    connection = db_worker.connection()
    checks = db_worker.get_url_check(connection, id)
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        "show_url.html",
        url_id=url[0],
        url=url,
        messages=messages,
        checks=checks
    )


@app.get("/urls")
def show_urls():
    connection = db_worker.connection()
    list_of_urls = db_worker.get_urls_checks_for_show_urls(connection)
    return render_template(
        "show_all_urls.html",
        checks=list_of_urls
    )


@app.post("/urls/<int:id>/checks")
def check_url(id):
    connection = db_worker.connection()
    url = db_worker.get_url_by_id(connection, id)
    url_id, url_name, url_created_at = url
    response = get_response(url_name)
    if not response:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for("show_url", id=id), 302)
    status_code = response.status_code
    tags_content = get_tags_content_from_response(response)
    check_result = {
        'url_id': url_id,
        'status_code': status_code,
        'h1': tags_content['h1'],
        'title': tags_content['title'],
        'description': tags_content['description'],
        'created_at': date.today(),
    }
    connection = db_worker.connection()
    db_worker.add_url_check(connection, check_result)
    flash("Страница успешно проверена", 'success')
    return redirect(url_for("show_url", id=id), 302)
