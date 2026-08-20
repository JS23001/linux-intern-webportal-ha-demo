import os
from datetime import date

import psycopg
from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")
SERVER_NAME = os.environ.get("SERVER_NAME", "ukendt webserver")


def get_entries():
    if not DATABASE_URL:
        return []
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, employee_name, work_date, hours, created_at
                FROM time_entries
                ORDER BY id DESC
                """
            )
            return cursor.fetchall()


@app.get("/health")
def health():
    if not DATABASE_URL:
        return {"status": "degraded", "database": "not configured"}, 503
    try:
        with psycopg.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_is_in_recovery(), now()")
                is_replica, checked_at = cursor.fetchone()
        return {
            "status": "ok",
            "web_server": SERVER_NAME,
            "database_role": "replica" if is_replica else "primary",
            "checked_at": checked_at.isoformat(),
        }
    except psycopg.Error as error:
        return {"status": "unhealthy", "database": str(error)}, 503


@app.get("/")
def index():
    try:
        entries = get_entries()
        database_error = None
    except psycopg.Error as error:
        entries = []
        database_error = str(error)
    return render_template(
        "index.html",
        entries=entries,
        database_error=database_error,
        server_name=SERVER_NAME,
        today=date.today().isoformat(),
    )


@app.post("/entries")
def create_entry():
    employee_name = request.form.get("employee_name", "").strip()
    work_date = request.form.get("work_date", "")
    hours = request.form.get("hours", "")

    if not employee_name or not work_date or not hours:
        abort(400, "Navn, dato og timer skal udfyldes.")

    try:
        hours_as_number = float(hours)
        if not 0 < hours_as_number <= 24:
            raise ValueError
    except ValueError:
        abort(400, "Timer skal være et tal mellem 0 og 24.")

    if not DATABASE_URL:
        abort(503, "Databasen er ikke konfigureret.")

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO time_entries (employee_name, work_date, hours)
                VALUES (%s, %s, %s)
                """,
                (employee_name, work_date, hours_as_number),
            )
        connection.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
