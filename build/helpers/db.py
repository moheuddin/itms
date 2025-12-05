import sqlite3
import os
import sys
import platform


# ---------------------------------------------------------
# 1) Resolve resource path (PyInstaller + Development)
# ---------------------------------------------------------
def resource_path(relative_path):
    """Return absolute path for both EXE and development."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)

    # Running from source
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


# ---------------------------------------------------------
# 2) DB path logic (different for dev vs EXE)
# ---------------------------------------------------------
def get_db_path():
    """
    Always load python.db from the application folder
    - Windows EXE → same folder as .exe
    - macOS .app → Contents/MacOS
    - Development → project folder
    """
    if getattr(sys, "frozen", False):
        # This works for:
        # - Windows PyInstaller EXE
        # - macOS MyApp.app/Contents/MacOS/app_binary
        app_dir = os.path.dirname(sys.executable)
        return os.path.join(app_dir, "python.db")

    # Development mode
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "..", "python.db")



# ---------------------------------------------------------
# 3) Database connection
# ---------------------------------------------------------
def get_connection():
    db_path = get_db_path()
    print("🚀 Using DB:", db_path)

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"❌ python.db not found at: {db_path}")

    conn = sqlite3.connect(
        db_path,
        check_same_thread=False,
        timeout=10.0
    )
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------
# 4) Helper functions
# ---------------------------------------------------------
def get_sections(category=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if category:
            cursor.execute(
                "SELECT DISTINCT section FROM article WHERE category=? ORDER BY section ASC",
                (category,)
            )
        else:
            cursor.execute("SELECT DISTINCT section FROM article ORDER BY section ASC")

        return [row["section"] for row in cursor.fetchall()]
    finally:
        conn.close()


def get_categories():
    return ["SRO", "Paripatra", "Circular", "ITA", "ITR", "Finance-Act", "Assessment"]
