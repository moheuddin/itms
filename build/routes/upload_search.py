from flask import Blueprint, request, jsonify
from helpers.db import get_connection
import json
import sqlite3

upload_search_bp = Blueprint("upload_search", __name__)

@upload_search_bp.route("/api/upload-files", methods=["GET"])
def api_upload_files():
    cat = request.args.get("cat", "").strip()
    mode = request.args.get("mode", "").strip()
    section = request.args.get("section", "").strip()

    conn = get_connection()
    conn.row_factory = sqlite3.Row  # dict-like rows
    try:
        with conn:
            cur = conn.cursor()

            # --- Category based fetch ---
            if cat:
                cur.execute("""
                    SELECT id, category, files, year, number, date, subject
                    FROM uploads
                    WHERE category = ?
                    ORDER BY date DESC
                """, (cat,))
                rows = cur.fetchall()

                data = []
                for row in rows:
                    try:
                        files_list = json.loads(row["files"]) if row["files"] else []
                    except json.JSONDecodeError:
                        files_list = []

                    data.append({
                        "id": row["id"],
                        "category": row["category"],
                        "files": files_list,
                        "year": row["year"],
                        "number": row["number"],
                        "date": row["date"],
                        "subject": row["subject"]
                    })

                return jsonify({"data": data})

            # --- Mode: years ---
            if mode == "years" and section:
                cur.execute("""
                    SELECT DISTINCT assessment_year FROM article
                    WHERE section = ? ORDER BY assessment_year ASC
                """, (section,))
                years = [r["assessment_year"] for r in cur.fetchall()]

                cur.execute("""
                    SELECT DISTINCT title FROM article WHERE section = ?
                """, (section,))
                titles = [r["title"] for r in cur.fetchall()]

                return jsonify({"years": years, "titles": titles})

            # Default: empty response
            return jsonify({"data": []})

    finally:
        conn.close()
