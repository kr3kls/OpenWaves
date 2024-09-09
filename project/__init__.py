import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from the .env file (if present)
load_dotenv()

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
login_manager = LoginManager()

login_manager.login_message = "Please log in to access this page."

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)

    # Specify the login view for unauthorized access
    login_manager.login_view = 'auth.login'  # Redirect to the login page if not logged in
    login_manager.login_message_category = 'danger'  # Bootstrap alert class for messages

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
