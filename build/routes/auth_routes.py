from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
import hashlib
import sqlite3
from helpers.db import get_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/verify_user", methods=["POST"])
def verify_user():
    email = request.form.get("email")
    password = request.form.get("password")
    captcha_input = request.form.get("captcha")

    errors = []

    # Debugging: print input
    print("Login attempt:", email, password, captcha_input)

    # if captcha_input.upper() != session.get('captcha', '').upper():
    #     errors.append("Invalid captcha.")

    if not email or not password:
        errors.append("Username and password are required.")

    user = None

    if not errors:
        hashed = hashlib.md5(password.encode()).hexdigest()
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed))
                row = cursor.fetchone()
                if row:
                    user = dict(row)
                    print("User found:", user)
            finally:
                cursor.close()

        if not user:
            errors.append("Invalid username or password.")

    if errors:
        print("Errors:", errors)
        return jsonify({"status": "failed", "errors": errors})

    session["user_id"] = user["id"]
    session["role"] = user.get("role", "user")
    session["email"] = user.get("email")

    print("Login success:", session)
    return jsonify({"status": "success", "role": session["role"]})


@auth_bp.route("/profile")
def user_profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("public.login"))
    return render_template("admin/profile.html", current_page="profile")


@auth_bp.route("/get_profile", methods=["GET"])
def get_profile():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"status": "failed", "message": "Not logged in"})

    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, name, email, role, status FROM users WHERE id=?", (user_id,))
            row = cursor.fetchone()
        finally:
            cursor.close()

    if not row:
        print("User not found:", user_id)
        return jsonify({"status": "failed", "message": "User not found"})

    user_data = {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "role": row["role"],
        "status": row["status"]
    }

    print("Get profile:", user_data)
    return jsonify({"status": "success", "user": user_data})


@auth_bp.route("/update_profile", methods=["POST"])
def update_profile():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"status": "failed", "message": "Not logged in"})

    name = request.form.get("name")
    email = request.form.get("email")
    role = request.form.get("role")
    status = request.form.get("status")
    password = request.form.get("password")

    hashed = hashlib.md5(password.encode()).hexdigest() if password else None

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            try:
                if hashed:
                    cursor.execute("""
                                   UPDATE users
                                   SET name=?,
                                       email=?,
                                       password=?
                                   WHERE id = ?
                                   """, (name, email, hashed, user_id))
                else:
                    cursor.execute("""
                                   UPDATE users
                                   SET name=?,
                                       email=?
                                   WHERE id = ?
                                   """, (name, email, user_id))
                conn.commit()
            finally:
                cursor.close()
    except sqlite3.OperationalError as e:
        return jsonify({"status": "failed", "message": f"DB locked: {e}"})

    session["email"] = email
    return jsonify({"status": "success"})
