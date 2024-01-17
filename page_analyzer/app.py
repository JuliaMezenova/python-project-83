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


load_dotenv()  # take environment variables from .env.

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)


@app.route("/")
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.post("/urls")
def add_url():
    url = request.form.get('url')
    normalized_url = normalize(url)
    errors = validate(normalized_url)
    if errors:
        flash(errors, 'errors')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            input_url=url,
            messages=messages
        ), 422
    with conn:
        with conn.cursor as curs:
            curs.execute(
                "SELECT * FROM urls WHERE name = %s;",
                (normalized_url,)
            )
            result_url = curs.fetchone()
            if result_url:
                flash("Cтраница уже существует", 'info')
                id = result_url.id
            else:
                curs.execute(
                    "INSERT INTO urls (name) VALUES (%s);",
                    (normalized_url,)
                )
                conn.commit()
                id = curs.fetchone()[0]
                curs.execute("SELECT * FROM urls WHERE id = %s;", (id,))
                result_url = curs.fetchone()
                flash("Страница успешно добавлена", 'success')
        curs.close()
    conn.close()
    return redirect(url_for('show_url', id=id))


@app.get("/urls/<int:id>")
def show_url(id):
    with conn:
        with conn.cursor as curs:
            curs.execute("SELECT * FROM urls WHERE id = %s;", (id,))
            result_url = curs.fetchone()
        curs.close()
    conn.close()
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        "show_url.html",
        url=result_url,
        messages=messages
    )


@app.get("/urls")
def show_urls():
    with conn:
        with conn.cursor as curs:
            curs.execute("SELECT * FROM urls ORDER BY id DESC;")
            result_urls = curs.fetchall()
        curs.close()
    conn.close()
    return render_template(
        "show_all_urls.html",
        urls=result_urls
    )
