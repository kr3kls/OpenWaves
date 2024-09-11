import os
from flask import Flask, g, request
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import secrets

# Load environment variables from the .env file (if present)
load_dotenv()

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
login_manager = LoginManager()

login_manager.login_message = "Please log in to access this page."

def create_app():
    # Explicitly set the template_folder path
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
    csrf = CSRFProtect(app)

    # Load config from environment variables, with default fallbacks
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///default.db')

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)

    # Specify the login view for unauthorized access
    login_manager.login_view = 'auth.login'  # Redirect to the login page if not logged in
    login_manager.login_message_category = 'danger'  # Bootstrap alert class for messages

    # Generate nonce for inline scripts
    @app.before_request
    def generate_nonce():
        g.csp_nonce = secrets.token_hex(16)  # 16-byte random nonce for each request

    # Set CSP headers after the request
    @app.after_request
    def set_csp_header(response):
        # Content Security Policy with violation reporting and support for inline styles with a nonce
        csp = (
            f"default-src 'self'; "  # Default policy: restrict all resources to self
            f"script-src 'self' 'nonce-{g.csp_nonce}'; "  # Allow inline scripts with nonce
            f"style-src 'self' 'nonce-{g.csp_nonce}' https://cdnjs.cloudflare.com; "  # Allow inline styles with nonce and external styles
            f"img-src 'self' data:; "  # Allow images from self and base64-encoded images
            f"object-src 'none'; "  # Disallow plugins like Flash
            f"base-uri 'self'; "  # Disallow forms being submitted to foreign origins
            f"form-action 'self'; "  # Only allow forms to submit to self
            f"frame-ancestors 'none'; "  # Prevent the page from being embedded in a frame
            f"report-uri /csp-violation-report-endpoint; "  # Send CSP violation reports here
        )
        response.headers['Content-Security-Policy'] = csp
        return response

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

@login_manager.user_loader
def load_user(user_id):
    # Import User inside the function to avoid circular import
    from .models import User
    return User.query.get(int(user_id))
