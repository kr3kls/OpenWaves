from flask import Blueprint, render_template, current_app
from flask_login import login_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    # TODO add logic to show user-specific data in the profile
    print(f"Looking for profile.html in: {current_app.jinja_loader.searchpath}")
    return render_template('profile.html')
