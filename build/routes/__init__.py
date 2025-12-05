from flask import Flask
from .public_routes import public_bp
from .auth_routes import auth_bp
#from .article_routes import article_bp
from .circular_routes import circular_bp
from .admin_routes import admin_bp           # main admin routes
from .admin_document import documents_bp    # admin document routes
from .upload_search import upload_search_bp

def register_routes(app: Flask):
    # Register all blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(circular_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(upload_search_bp)

    # Apply login protection to all admin blueprints
#    admin_blueprints = [admin_bp, documents_bp]  # add more admin BPs if needed
#    for bp in admin_blueprints:
#        bp.before_request(login_required)
