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
                flash("Cтраница уже существует", 'info')
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
            curs.execute("SELECT * FROM urls ORDER BY id DESC;")
            result = curs.fetchall()
    return render_template(
        "show_all_urls.html",
        urls=result
    )


@app.post("/urls/<int:id>/checks")
def check_url(id):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute("SELECT * FROM urls WHERE id = %s;", (id, ))
            url_id = curs.fetchone()[0]
            curs.execute(
                "INSERT INTO url_checks \
                (url_id, status_code, h1, title, description, created_at) \
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
                (url_id, 200, 'h1', 'title', 'description', date.today())
            )
    flash("Страница успешно проверена", 'success')
    return redirect(url_for("show_url", id=id), 302)
