from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # check session
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('public.login'))  # adjust your login route
        return f(*args, **kwargs)
    return decorated_function
