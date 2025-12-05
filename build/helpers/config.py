import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))   # /pythondemo

# Final correct upload folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

# Ensure folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)