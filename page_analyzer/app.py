from flask import (
    Flask,
    render_template,
    request,
    flash,
    get_flashed_messages,
    url_for,
    redirect
)
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
from .validator import validate
from .normalizator import normalize
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
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute(
                "SELECT * FROM urls WHERE name = %s;",
                (normalized_url, )
            )
            result = curs.fetchone()  # тут будет кортеж
            if result:
                flash("Страница уже существует", 'info')
                id = result[0]
            else:
                curs.execute(
                    "INSERT INTO urls (name, created_at) \
                    VALUES (%s, %s) RETURNING id;",
                    (normalized_url, date.today())
                )
                conn.commit()
                id = curs.fetchone()[0]
                flash("Страница успешно добавлена", 'success')

    return redirect(url_for('show_url', id=id), 302)


@app.get("/urls/<int:id>")
def show_url(id):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute("SELECT * FROM urls WHERE id = %s;", (id, ))
            url = curs.fetchone()
            curs.execute(
                "SELECT id, url_id, status_code, h1, title, \
                description, created_at FROM url_checks WHERE url_id = %s \
                ORDER BY id DESC;", (id, )
            )
            checks = curs.fetchall()
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
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute("SELECT urls.id, urls.name, url_checks.created_at, \
                url_checks.status_code \
                FROM urls AS urls LEFT JOIN \
                (SELECT DISTINCT ON (url_checks.url_id) \
                url_checks.url_id, url_checks.status_code, \
                url_checks.created_at FROM url_checks \
                ORDER BY url_checks.url_id ASC, url_checks.created_at DESC) \
                AS url_checks ON urls.id = url_checks.url_id \
                ORDER BY urls.id DESC;")
            urls = curs.fetchall()
            list_of_urls = []
            for url in urls:
                list_of_urls.append({
                    'id': url[0],
                    'name': url[1],
                    'date_of_last_check': url[2],
                    'status_code': url[3],
                })

    return render_template(
        "show_all_urls.html",
        urls=urls,
        checks=list_of_urls
    )


@app.post("/urls/<int:id>/checks")
def check_url(id):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute("SELECT * FROM urls WHERE id = %s;", (id, ))
            url_id, url_name, url_created_at = curs.fetchone()

            response = get_response(url_name)
            if not response:
                flash('Произошла ошибка при проверке', 'error')
                return redirect(url_for("show_url", id=id), 302)
            status_code = response.status_code
            tags_content = get_tags_content_from_response(response)
            curs.execute(
                "INSERT INTO url_checks \
                (url_id, status_code, h1, title, description, created_at) \
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;", (
                    url_id,
                    status_code,
                    tags_content['h1'],
                    tags_content['title'],
                    tags_content['description'],
                    date.today()
                )
            )
    flash("Страница успешно проверена", 'success')
    return redirect(url_for("show_url", id=id), 302)
