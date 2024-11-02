"""
Configuration file for Flask application.

This module contains the `Config` class that holds all configuration
settings for the Flask application, including file upload settings, 
security settings, database configuration, and more.

Configurations are loaded from environment variables when available, 
with sensible default values to fall back on.
"""

import os

class Config:
    """
    Configuration settings for the Flask application.

    Attributes:
        UPLOAD_FOLDER (str): Directory to store uploaded files.
        ALLOWED_EXTENSIONS (set): Allowed file extensions for uploads.
        SECRET_KEY (str): Secret key for session management and CSRF protection.
        SQLALCHEMY_DATABASE_URI (str): Database connection URI.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Disable or enable track modifications.
        WTF_CSRF_ENABLED (bool): Enable CSRF protection for forms.
        CSP_* (str): Content Security Policy settings.
        LOGIN_VIEW (str): Default view for user login redirection.
        LOGIN_MESSAGE (str): Message displayed when login is required.
        LOGIN_MESSAGE_CATEGORY (str): Bootstrap alert category for login messages.
    """
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'openwaves/static/images/diagrams')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///default.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CSRF protection
    WTF_CSRF_ENABLED = True

    # Content Security Policy settings
    CSP_DEFAULT_SRC = "'self'"
    CSP_SCRIPT_SRC = "'self'"
    CSP_STYLE_SRC = "'self' https://cdnjs.cloudflare.com"
    CSP_IMG_SRC = "'self' data:"
    CSP_OBJECT_SRC = "'none'"
    CSP_BASE_URI = "'self'"
    CSP_FORM_ACTION = "'self'"
    CSP_FRAME_ANCESTORS = "'none'"
    CSP_REPORT_URI = "/csp-violation-report-endpoint"

    # Login settings
    LOGIN_VIEW = 'auth.login'
    LOGIN_MESSAGE = "Please log in to access this page."
    LOGIN_MESSAGE_CATEGORY = 'danger'

    SERVER_NAME = f"{os.getenv('SERVER_NAME', '127.0.0.1')}:{os.getenv('SERVER_PORT', '5000')}"
