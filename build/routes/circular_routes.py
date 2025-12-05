from flask import Blueprint, render_template, request, jsonify, session
import os, json
import sqlite3
from helpers.db import get_connection, get_categories
from helpers.uploads import save_uploaded_files
from helpers.config import UPLOAD_FOLDER
from helpers.auth import login_required

circular_bp = Blueprint("circular", __name__, url_prefix="/admin")


def delete_files(file_list):
    for f in file_list:
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, f))
        except FileNotFoundError:
            pass


@circular_bp.route("/circular", methods=["GET"])
@login_required
def view_circulars():
    #    if session.get("role") != "admin":
    #        return redirect(url_for("public.login"))

    categories = get_categories()
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM uploads ORDER BY id DESC")
    rows = cursor.fetchall()

    uploads = []
    for row in rows:
        row_dict = dict(row)
        try:
            row_dict["files"] = json.loads(row_dict["files"])
        except json.JSONDecodeError:
            row_dict["files"] = []
        uploads.append(row_dict)

    conn.close()

    return render_template(
        "admin/circular.html",
        uploads=uploads,
        current_page="circular",
        categories=categories
    )


# -------------------------
# Add or Edit Circular (AJAX)
# -------------------------
@circular_bp.route("/circular/save", methods=["POST"])
@login_required
def save_circular():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    circular_id = request.form.get("id")
    category = request.form.get("category")
    number = request.form.get("number")
    year = request.form.get("year")
    date = request.form.get("date")
    subject = request.form.get("subject")
    uploaded_files = save_uploaded_files(request.files.getlist("files[]"), UPLOAD_FOLDER)

    conn = get_connection()
    cursor = conn.cursor()

    if circular_id:  # Edit
        cursor.execute("SELECT files FROM uploads WHERE id=?", (circular_id,))
        row = cursor.fetchone()
        existing_files = json.loads(row["files"]) if row and row["files"] else []
        all_files = existing_files + uploaded_files

        cursor.execute("""
                       UPDATE uploads
                       SET category=?,
                           number=?,
                           year=?,
                           date=?,
                           subject=?,
                           files=?
                       WHERE id = ?
                       """, (category, number, year, date, subject, json.dumps(all_files), circular_id))

        message = "Circular updated!"
    else:  # Add new
        cursor.execute("""
                       INSERT INTO uploads (category, number, year, date, subject, files)
                       VALUES (?, ?, ?, ?, ?, ?)
                       """, (category, number, year, date, subject, json.dumps(uploaded_files)))
        message = "Circular added!"

    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": message})


# -------------------------
# Delete Entire Circular (AJAX)
# -------------------------
@circular_bp.route("/circular/delete", methods=["POST"])
@login_required
def delete_circular():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    circular_id = request.form.get("id")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT files FROM uploads WHERE id=?", (circular_id,))
    row = cursor.fetchone()
    if row and row["files"]:
        delete_files(json.loads(row["files"]))

    cursor.execute("DELETE FROM uploads WHERE id=?", (circular_id,))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Circular deleted!"})


# -------------------------
# Delete Single File (AJAX)
# -------------------------
@circular_bp.route("/circular/delete-file", methods=["POST"])
@login_required
def delete_file():
    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    file_id = request.form.get("id")
    file_name = request.form.get("file")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT files FROM uploads WHERE id=?", (file_id,))
    row = cursor.fetchone()
    files = json.loads(row["files"]) if row and row["files"] else []

    files = [f for f in files if f != file_name]
    cursor.execute("UPDATE uploads SET files=? WHERE id=?", (json.dumps(files), file_id))
    delete_files([file_name])
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "File deleted!"})
