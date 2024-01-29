import psycopg2
from contextlib import contextmanager
import os
from datetime import date


@contextmanager
def connection():
    database_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(database_url)
    try:
        yield conn
    finally:
        conn.close()


def get_url_by_name(connection, normalized_url):
    with connection as conn:
        with conn.cursor() as curs:
            curs.execute(
                "SELECT * FROM urls WHERE name = %s;",
                (normalized_url, )
            )
            url = curs.fetchone()
    return url


def get_url_by_id(connection, id):
    with connection as conn:
        with conn.cursor() as curs:
            curs.execute("SELECT * FROM urls WHERE id = %s;", (id, ))
            url = curs.fetchone()
    return url


def add_url_to_db_urls(connection, normalized_url):
    with connection as conn:
        with conn.cursor() as curs:
            curs.execute(
                "INSERT INTO urls (name, created_at) \
                VALUES (%s, %s) RETURNING id;",
                (normalized_url, date.today())
            )
            conn.commit()
            id = curs.fetchone()[0]
    return id


def get_url_check(connection, id):
    with connection as conn:
        with conn.cursor() as curs:
            curs.execute(
                "SELECT id, url_id, status_code, h1, title, \
                description, created_at FROM url_checks WHERE url_id = %s \
                ORDER BY id DESC;", (id, )
            )
            checks = curs.fetchall()
    return checks


def get_urls_checks_for_show_urls(connection):
    with connection as conn:
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
        return list_of_urls


def add_url_check(connection, check_result):
    with connection as conn:
        with conn.cursor() as curs:
            curs.execute(
                "INSERT INTO url_checks \
                (url_id, status_code, h1, title, description, created_at) \
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;", (
                    check_result['url_id'],
                    check_result['status_code'],
                    check_result['h1'],
                    check_result['title'],
                    check_result['description'],
                    check_result['created_at'],
                )
            )
            conn.commit()
