"""File: __init__.py

    This file contains the initialization methods for the application.
"""

import os
import secrets
from flask import Flask, g
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from .config import Config

# Load environment variables from the .env file (if present)
load_dotenv()

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(test_config=None):
    """Standard method to create Flask app."""
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
    app.config.from_object(Config)

    # Apply test config if provided
    if test_config:
        app.config.update(test_config)

    _csrf = CSRFProtect(app)

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)

    # Configure Login Manager settings
    login_manager.login_view = app.config['LOGIN_VIEW']
    login_manager.login_message = app.config['LOGIN_MESSAGE']
    login_manager.login_message_category = app.config['LOGIN_MESSAGE_CATEGORY']

    # Generate nonce for inline scripts
    @app.before_request
    def generate_nonce():
        g.csp_nonce = secrets.token_hex(16)  # 16-byte random nonce for each request

    # Set CSP headers after the request
    @app.after_request
    def set_csp_header(response):
        csp = (
            f"default-src {app.config['CSP_DEFAULT_SRC']}; "
            f"script-src {app.config['CSP_SCRIPT_SRC']} 'nonce-{g.csp_nonce}'; "
            f"style-src {app.config['CSP_STYLE_SRC']} 'nonce-{g.csp_nonce}'; "
            f"img-src {app.config['CSP_IMG_SRC']}; "
            f"object-src {app.config['CSP_OBJECT_SRC']}; "
            f"base-uri {app.config['CSP_BASE_URI']}; "
            f"form-action {app.config['CSP_FORM_ACTION']}; "
            f"frame-ancestors {app.config['CSP_FRAME_ANCESTORS']}; "
            f"report-uri {app.config['CSP_REPORT_URI']}; "
        )
        response.headers['Content-Security-Policy'] = csp
        return response

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint  # pylint: disable=C0415,R0401
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint  # pylint: disable=C0415,R0401
    app.register_blueprint(main_blueprint)

    return app

@login_manager.user_loader
def load_user(user_id):
    """Method to avoid circular import for User"""
    from .models import User  # pylint: disable=C0415,R0401
    return db.session.get(User, int(user_id))
