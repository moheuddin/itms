import os
from datetime import datetime
from werkzeug.utils import secure_filename

def save_uploaded_files(file_list, upload_path):
    saved_files = []

    # Ensure folder exists
    os.makedirs(upload_path, exist_ok=True)

    for f in file_list:
        if f.filename:
            filename = f"{int(datetime.now().timestamp())}_{secure_filename(f.filename)}"
            f.save(os.path.join(upload_path, filename))
            saved_files.append(filename)

    return saved_files
