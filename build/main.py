import sys
import threading
import socket
import time
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
from flask import Flask
from routes import register_routes
from helpers.license import verify_license

# ----------------------------------------
# License check
# ----------------------------------------
# if not verify_license():
#     messagebox.showerror(
#         "License Error",
#         "❌ Software not activated or running on an unauthorized computer.\n"
#         "Please run Activation.exe first."
#     )
#     sys.exit(1)

# ----------------------------------------
# Configuration
# ----------------------------------------
LOGIN_BUTTON_DISABLED = False  # existing global
PROTECT_ENABLED = False        # global for templates only
FLASK_DEBUG = True            # enable debug mode

# ----------------------------------------
# Flask app setup
# ----------------------------------------
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = "your_secret_key_here"
app.config["LOGIN_BUTTON_DISABLED"] = LOGIN_BUTTON_DISABLED

@app.context_processor
def inject_globals():
    return dict(
        disable_login_button=app.config.get("LOGIN_BUTTON_DISABLED", False),
        protect_enabled=PROTECT_ENABLED
    )

register_routes(app)

# ----------------------------------------
# Single instance check
# ----------------------------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.bind(("127.0.0.1", 65432))
except OSError:
    print("Another instance is already running!")
    sys.exit()

# ----------------------------------------
# Tkinter Launcher GUI
# ----------------------------------------
def create_launcher():
    root = tk.Tk()
    root.title("ITMS Launcher")
    root.geometry("300x150")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    frame = ttk.Frame(root, padding=20)
    frame.pack(expand=True, fill="both")

    # Loading label with spinner
    spinner_cycle = ["⏳", "⌛", "🔄"]
    loading_label = ttk.Label(frame, text="Starting server... ⏳", anchor="center", font=("Arial", 12))
    loading_label.pack(pady=20, fill="x")

    # Open ITMS button (disabled initially)
    btn_open = ttk.Button(
        frame,
        text="Open ITMS",
        state="disabled",
        command=lambda: webbrowser.open("http://127.0.0.1:8000")
    )
    btn_open.pack(pady=10, fill="x")

    # Close button with confirmation
    def on_close():
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?"):
            root.destroy()

    btn_close = ttk.Button(
        frame,
        text="Close",
        command=on_close
    )
    btn_close.pack(pady=10, fill="x")

    # Bind the window close (X) button to the same confirmation
    root.protocol("WM_DELETE_WINDOW", on_close)

    # ----------------------------------------
    # Run Flask server in background (debug mode)
    # ----------------------------------------
    def run_flask():
        app.run(debug=FLASK_DEBUG, host="127.0.0.1", port=8000, use_reloader=False)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # ----------------------------------------
    # Poll server readiness
    # ----------------------------------------
    def check_server_ready():
        i = 0
        while True:
            try:
                with socket.create_connection(("127.0.0.1", 8000), timeout=1):
                    btn_open.config(state="normal")
                    loading_label.config(text="Server is ready! ✅")
                    break
            except OSError:
                loading_label.config(text=f"Starting server... {spinner_cycle[i % len(spinner_cycle)]}")
                i += 1
                time.sleep(0.3)

    poll_thread = threading.Thread(target=check_server_ready, daemon=True)
    poll_thread.start()

    root.mainloop()


# ----------------------------------------
# Run Launcher
# ----------------------------------------
if __name__ == "__main__":
    create_launcher()
