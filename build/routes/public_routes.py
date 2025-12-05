from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, current_app, flash
import sqlite3
from helpers.db import get_connection
import os
import math



public_bp = Blueprint("public", __name__)


# -------------------
# Mapping Page
# -------------------
@public_bp.route("/mapping")
def mapping():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 🔍 Print actual DB file
        cursor.execute("PRAGMA database_list;")
        db_info = cursor.fetchall()
        print("📌 Using DB file:", db_info[0][2])

        # 🔍 Your actual query
        cursor.execute("SELECT DISTINCT incometax84 FROM mapping_table ORDER BY incometax84 ASC")
        rows = cursor.fetchall()
        unique_values = [row[0] for row in rows]

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    return render_template("mapping.html", active_page="mapping", mapping_values=unique_values)

# Search mapping in database via AJAX
# -------------------
# -------------------
# Search mapping in database via AJAX (exact match)
# -------------------
@public_bp.route('/search-map', methods=['POST'])
def search_map():

    search_value = request.form.get('search_value', '').strip()
    if not search_value:
        return jsonify([])

    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Exact match query
        query = "SELECT * FROM mapping_table WHERE incometax84 = ?"
        cursor.execute(query, (search_value,))
        rows = cursor.fetchall()

        # Convert rows to list of dicts
        columns = [description[0] for description in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]

        # # Optional: clean NaN values
        # for row in result:
        #     for key, value in row.items():
        #         if isinstance(value, float) and math.isnan(value):
        #             row[key] = ""
        #         elif isinstance(value, float) and not math.isnan(value):
        #             row[key] = int(value) if value.is_integer() else round(value, 2)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@public_bp.route("/finance-act")
def finance_act():
    return render_template("finance-act.html", active_page="finance-act")
# -------------------
# Public Pages
# -------------------
@public_bp.route("/")
def home():
    disable_login_button = current_app.config.get("LOGIN_BUTTON_DISABLED", False)
    return render_template("index.html", active_page="home",disable_login_button=disable_login_button)

@public_bp.route("/ita")
def ita():
    print(request.args)
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT section FROM article  WHERE category='ITA'  ORDER BY section ASC")
        rows = cursor.fetchall()
        sections = [row["section"] for row in rows]
    finally:
        cursor.close()
        conn.close()
    return render_template("ita.html", active_page="ita", sections=sections)
@public_bp.route("/itr")
def itr():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT DISTINCT section FROM article WHERE category='ITR' ORDER BY section ASC"
        )
        rows = cursor.fetchall()
        sections = [row["section"] for row in rows]
    finally:
        cursor.close()
        conn.close()

    # Render the template with fetched sections
    return render_template("itr.html", active_page="itr", sections=sections)


@public_bp.route("/tds")
def tds():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT section FROM article  WHERE category='TDS' ORDER BY section ASC")
        rows = cursor.fetchall()
        sections = [row["section"] for row in rows]
    finally:
        cursor.close()
        conn.close()
    return render_template("tds.html", active_page="tds",sections=sections)

@public_bp.route("/adr")
def adr():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT section FROM article  WHERE category='ADR'  ORDER BY section ASC")
        rows = cursor.fetchall()
        sections = [row["section"] for row in rows]
    finally:
        cursor.close()
        conn.close()
    return render_template("adr.html", active_page="adr",sections=sections)

@public_bp.route("/sro")
def sro():
    return render_template("sro.html", active_page="sro")

@public_bp.route("/paripatra")
def paripatra():
    return render_template("paripatra.html", active_page="paripatra")

@public_bp.route("/circular")
def circular_page():
    return render_template("circular.html", active_page="circular")

@public_bp.route("/circular/<int:id>")
def circular_single(id):
    return render_template("circular_single.html", id=id, active_page="circular")

@public_bp.route("/jurisdiction")
def jurisdiction():

    return render_template("jurisdiction.html", active_page="jurisdiction")

@public_bp.route("/assessment")
def assessment():
    return render_template("assessment.html", active_page="assessment")

@public_bp.route("/tax-code")
def tax_code_page():
    return render_template("tax-code.html", active_page="tax-code")

@public_bp.route("/tax-rate")
def tax_rate():
    return render_template("tax-rate.html", active_page="tax_rate")

# -------------------
# Contact Page + AJAX
# -------------------
@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        captcha_input = request.form.get("captcha")

        if not captcha_input or captcha_input.upper() != session.get("captcha", "").upper():
            return jsonify({"status": "failed", "message": "Invalid CAPTCHA."})

        if not name or not email or not message:
            return jsonify({"status": "failed", "message": "All fields are required."})

        return jsonify({"status": "success", "message": "Message sent successfully!"})

    return render_template("contact.html", active_page="contact")

# -------------------
# Login / Logout
# -------------------
@public_bp.route("/login")
def login():
    # Check if login is disabled from main.py config
    if current_app.config.get("LOGIN_BUTTON_DISABLED", False):
        flash("Login is temporarily disabled.", "warning")  # optional flash message
        return redirect(url_for("public.home"))  # redirect to home or any page
    return render_template("login.html", active_page="login")

@public_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("public.home"))

# -------------------
# CAPTCHA Route
# -------------------
@public_bp.route("/captcha")
def captcha():
    return generate_captcha()

# -------------------
# AJAX Search API (ITA Page)
# -------------------
# @public_bp.route("/api/search")
# def search():
#     mode = request.args.get("mode", "").strip()
#     conn = get_connection()
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()
#
#     try:
#         if mode != "search":
#             return jsonify({"error": "Invalid mode"}), 400
#
#         # Get search parameters
#         section = request.args.get("section", "").strip()
#         category = request.args.get("category", "").strip()
#         year = request.args.get("year", "").strip()
#         title = request.args.get("title", "").strip()
#         content = request.args.get("content", "").strip()
#
#         # Base query
#         query = "SELECT * FROM article WHERE 1=1"
#         params = []
#
#         # Apply filters only if provided
#         if category:
#             query += " AND category=?"
#             params.append(category)
#         if year:
#             query += " AND assessment_year=?"
#             params.append(year)
#         if section:
#             query += " AND section=?"
#             params.append(section)  # exact match for section
#         if title:
#             query += " AND title LIKE ?"
#             params.append(f"%{title}%")
#         if content:
#             query += " AND content LIKE ?"
#             params.append(f"%{content}%")
#
#         print("Section",params)
#
#         cursor.execute(query, params)
#         results = [dict(row) for row in cursor.fetchall()]
#
#         if not results:
#             return jsonify({"message": "No articles found", "results": []})
#
#         return jsonify({"results": results})
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
#     finally:
#         cursor.close()
#         conn.close()

