
import os
import sqlite3
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-only-change-this-secret"
)

DATABASE = os.environ.get(
    "DATABASE_PATH",
    str(Path(__file__).resolve().parent / "internships.db")
)

STATUSES = ["Applied", "Interview", "Offered", "Completed", "Rejected"]


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS internships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                student_email TEXT NOT NULL,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Applied'
            )
        """)


@app.route("/")
def index():
    with get_db() as db:
        students = db.execute(
            "SELECT * FROM internships ORDER BY id DESC"
        ).fetchall()

    counts = {status: 0 for status in STATUSES}
    for student in students:
        if student["status"] in counts:
            counts[student["status"]] += 1

    return render_template(
        "index.html",
        students=students,
        counts=counts,
        statuses=STATUSES
    )


@app.route("/add", methods=["POST"])
def add_student():
    fields = [
        request.form.get("student_name", "").strip(),
        request.form.get("student_email", "").strip(),
        request.form.get("company", "").strip(),
        request.form.get("role", "").strip(),
    ]
    status = request.form.get("status", "Applied")

    if not all(fields):
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("index"))

    if status not in STATUSES:
        flash("Invalid internship status.", "error")
        return redirect(url_for("index"))

    with get_db() as db:
        db.execute(
            """INSERT INTO internships
               (student_name, student_email, company, role, status)
               VALUES (?, ?, ?, ?, ?)""",
            (*fields, status)
        )

    flash("Internship record added successfully.", "success")
    return redirect(url_for("index"))


@app.route("/health")
def health():
    return {"status": "healthy"}, 200


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
