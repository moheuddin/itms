# admin_routes.py
from flask import Blueprint, render_template, session, redirect, url_for

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# -----------------------------
# Admin Dashboard
# -----------------------------
@admin_bp.route("/index")
def admin_index():
    if session.get("role") != "admin":
        return redirect(url_for("public.login"))
    return render_template("admin/index.html", current_page="index", user=session.get("user_id"))


# -----------------------------
# Admin Circular Page
# -----------------------------
@admin_bp.route("/circular")
def admin_circular():
    if session.get("role") != "admin":
        return redirect(url_for("public.login"))
    return render_template("admin/circular.html", current_page="circular", user=session.get("user_id"))


# -----------------------------
# Admin Logout
# -----------------------------
@admin_bp.route("/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("public.login"))
