from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import json
import sqlite3
from helpers.db import get_connection, get_sections
from helpers.auth import login_required
import re

documents_bp = Blueprint("admin_document", __name__, url_prefix="/admin/document")
DOCUMENT_CATEGORIES = [
    "ITA",
    "ITR",
    "TDS",
    "ADR"
]


# -------------------------
# Admin document page
# -------------------------
@documents_bp.route("/", methods=["GET"])
@login_required
def admin_document():
    category = request.args.get("category", "").strip()  # always applied
    sections = get_sections(category)
    return render_template(
        "admin/document.html",
        current_page="document",
        user=session.get("user_id"),
        sections=sections
    )


# -------------------------
# Add new article
# -------------------------
@documents_bp.route("/add", methods=["GET", "POST"])
def add_article():
    category = request.args.get("category", "").strip()  # always applied
    sections = get_sections(category)
    assessment_years = generate_assessment_years()

    if request.method == "POST":
        category = request.form.get("category")
        section = request.form.get("section")
        assessment_year = request.form.get("assessment_year")
        title = request.form.get("title")
        content = request.form.get("content")

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                           INSERT INTO article (category, section, assessment_year, title, content)
                           VALUES (?, ?, ?, ?, ?)
                           """, (category, section, assessment_year, title, content))
            conn.commit()
            return jsonify({"status": "success", "message": "Article added successfully."})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        finally:
            conn.close()

    return render_template(
        "admin/pertial_document_form.html",
        current_page="document",
        user=session.get("user_id"),
        sections=sections,
        assessment_years=assessment_years,
        categories=DOCUMENT_CATEGORIES,  # << Add this
    )


# -------------------------
# Edit article
# -------------------------
@documents_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_article(id):
    # --- GET: load article + helpers for form ---
    conn = get_connection()
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # fetch the article row (must include old_section column in DB)
        cursor.execute("SELECT * FROM article WHERE id = ?", (id,))
        article = cursor.fetchone()

        # fetch distinct sections / years for select boxes
        cursor.execute("SELECT DISTINCT section FROM article ORDER BY section ASC")
        sections = [row["section"] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT assessment_year FROM article ORDER BY assessment_year DESC")
        assessment_years = [row["assessment_year"] for row in cursor.fetchall()]
    finally:
        conn.close()

    # --- POST: update article fields including old_section ---
    if request.method == "POST":
        # Read form fields (strip to avoid leading/trailing spaces)
        category = (request.form.get("category") or "").strip()
        section = (request.form.get("section") or "").strip()
        old_section = (request.form.get("old_section") or "").strip()
        assessment_year = (request.form.get("assessment_year") or "").strip()
        title = (request.form.get("title") or "").strip()
        content = request.form.get("content") or ""

        # Optionally validate required fields here
        # e.g., if not section: return jsonify({"status":"error", "message":"Section required"}), 400

        conn = get_connection()
        try:
            cursor = conn.cursor()

            # Ensure the article table has an 'old_section' column.
            # Update article including old_section.
            cursor.execute("""
                           UPDATE article
                           SET category        = ?,
                               section         = ?,
                               old_section     = ?,
                               assessment_year = ?,
                               title           = ?,
                               content         = ?
                           WHERE id = ?
                           """, (category, section, old_section, assessment_year, title, content, id))

            conn.commit()
            return jsonify({"status": "success", "message": "Article updated successfully."})
        except Exception as e:
            # Log the exception if you have logging; return message to client
            return jsonify({"status": "error", "message": str(e)})
        finally:
            conn.close()

    # --- Render template for GET ---
    return render_template(
        "admin/pertial_document_form.html",
        current_page="document",
        user=session.get("user_id"),
        sections=sections,
        assessment_years=assessment_years,
        article=article,
        edit_mode=True,
        categories=DOCUMENT_CATEGORIES,
    )


# -------------------------
# Delete article
# -------------------------
@documents_bp.route("/delete/<int:id>", methods=["POST"])
def delete_article(id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM article WHERE id=?", (id,))
        conn.commit()
        return jsonify({"status": "success", "message": f"Article {id} deleted successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        conn.close()


# -------------------------
# Detail article
# -------------------------
@documents_bp.route("/detail-article/<int:id>")
def detail_article(id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM article WHERE id=?", (id,))
    article = cursor.fetchone()

    cursor.close()
    conn.close()

    if not article:
        return redirect(url_for('admin_document.admin_document'))

    return render_template("admin/document_detail.html", article=article)


# -------------------------
# Generate assessment years
# -------------------------
def generate_assessment_years():
    english_years = [f"{y}-{str(y + 1)[-2:]}" for y in range(2015, 2023)]
    bengali_digits = {'0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪', '5': '৫', '6': '৬', '7': '৭', '8': '৮',
                      '9': '৯'}

    def to_bengali(num_str):
        return ''.join(bengali_digits.get(c, c) for c in num_str)

    bengali_years = [f"{to_bengali(str(y))}-{to_bengali(str(y + 1)[-2:])}" for y in range(2022, 2051)]
    return english_years + bengali_years


# -------------------------
# Combined API route
# -------------------------
@documents_bp.route("/api", methods=["GET"])
def articles_api():
    mode = request.args.get("mode", "").strip()
    section = request.args.get("section", "").strip()
    year = request.args.get("year", "").strip()
    title = request.args.get("title", "").strip()
    content = request.args.get("content", "").strip()
    category = request.args.get("category", "").strip()  # always applied

    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    def extract_year(fin_year):
        if not fin_year or not isinstance(fin_year, str):
            return 0
        first = fin_year.split("-")[0].strip()
        bangla = "০১২৩৪৫৬৭৮৯"
        english = "0123456789"
        first = first.translate(str.maketrans(bangla, english))
        first = re.sub(r"\D", "", first)
        return int(first) if first.isdigit() else 0

    try:
        if mode == "getTitle":
            cursor.execute(
                "SELECT DISTINCT title FROM article WHERE category = ? ORDER BY title ASC",
                (category,)
            )
            titles = [row["title"] for row in cursor.fetchall()]
            return jsonify({"titles": titles})

        if mode == "years" and section:
            cursor.execute("""
                           SELECT DISTINCT assessment_year
                           FROM article
                           WHERE (section = ? OR old_section = ?)
                             AND category = ?
                           ORDER BY assessment_year DESC
                           """, (section, section, category))
            years = [row["assessment_year"] for row in cursor.fetchall()]

            cursor.execute("""
                           SELECT DISTINCT title
                           FROM article
                           WHERE (section = ? OR old_section = ?)
                             AND category = ?
                           ORDER BY title ASC
                           """, (section, section, category))
            titles = [row["title"] for row in cursor.fetchall()]

            return jsonify({"years": years, "titles": titles})

        if mode == "search":
            result_rows = []

            # Build base query
            query = "SELECT * FROM article WHERE category = ?"
            params = [category]

            if section:
                query += " AND section = ?"
                params.append(section)

            cursor.execute(query, params)
            main_rows = cursor.fetchall()
            main_dict_rows = [dict(r) for r in main_rows]
            result_rows.extend(main_dict_rows)

            # Collect unique old_sections from main_rows
            old_sections = set()
            for r_dict in main_dict_rows:
                old_sec = (r_dict.get("old_section") or "").strip()
                if old_sec:
                    old_sections.add(old_sec)

            # Pull rows for each old_section
            for old_sec in old_sections:
                cursor.execute(
                    "SELECT * FROM article WHERE section = ? AND category = ?",
                    (old_sec, category)
                )
                extra_rows = cursor.fetchall()
                result_rows.extend([dict(r) for r in extra_rows])

            # Add _sort_column
            for r in result_rows:
                r["_sort_column"] = extract_year(r.get("assessment_year"))

            # Apply filters
            if year:
                result_rows = [r for r in result_rows if r.get("assessment_year") == year]
            if title:
                result_rows = [r for r in result_rows if r.get("title") == title]
            if content:
                result_rows = [r for r in result_rows if content.lower() in (r.get("content") or "").lower()]

            # Sort by year descending
            result_rows.sort(key=lambda x: x["_sort_column"], reverse=True)

            # Remove helper column
            for r in result_rows:
                r.pop("_sort_column", None)

            return jsonify({"results": result_rows})

        return jsonify({"error": "Invalid mode"}), 400

    finally:
        cursor.close()
        conn.close()


@documents_bp.route("/fetch", methods=["GET"])
def fetch_articles():
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 20))
    order_column_index = int(request.args.get('order[0][column]', 0))
    order_dir = request.args.get('order[0][dir]', 'asc')
    search_value = request.args.get('search[value]', '')

    # Corrected: match the JS parameter name
    section_filter = request.args.getlist('section[]')
    columns = ['id', 'category', 'section', 'title', 'assessment_year']
    order_column = columns[order_column_index] if order_column_index < len(columns) else 'section'

    connection = get_connection()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        # Build WHERE clause
        where_clauses = []
        params = []

        if search_value:
            where_clauses.append("(title LIKE ? OR section LIKE ? OR category LIKE ?)")
            params.extend([f"%{search_value}%", f"%{search_value}%", f"%{search_value}%"])

        if section_filter:
            placeholders = ','.join(['?'] * len(section_filter))
            where_clauses.append(f"section IN ({placeholders})")
            params.extend(section_filter)

        # Join clauses with AND
        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        # Total records
        cursor.execute("SELECT COUNT(*) AS total FROM article")
        total_records = cursor.fetchone()['total']

        # Filtered records
        if where_sql:
            cursor.execute(f"SELECT COUNT(*) AS total FROM article {where_sql}", params)
            records_filtered = cursor.fetchone()['total']
        else:
            records_filtered = total_records

        # Fetch paginated data
        sql = f"SELECT * FROM article {where_sql} ORDER BY {order_column} {order_dir} LIMIT ? OFFSET ?"
        params.extend([length, start])
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        data = []
        for row in rows:
            data.append({
                "id": row['id'],
                "category": row['category'],
                "section": row['section'],
                "title": row['title'],
                "assessment_year": row['assessment_year'],
                "detail": f'<a href="detail-article/{row["id"]}">Detail</a>',
                "edit": f'<a href="edit/{row["id"]}">Edit</a>',
                "delete": f'<a href="delete/{row["id"]}" onclick="return confirm(\'Are you sure?\')">Delete</a>'
            })
    finally:
        connection.close()

    return jsonify({
        "draw": int(request.args.get('draw', 0)),
        "recordsTotal": total_records,
        "recordsFiltered": records_filtered,
        "data": data
    })
