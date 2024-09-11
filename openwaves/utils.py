from werkzeug.security import generate_password_hash
from . import db 

def update_user_password(user, new_password):
    # Generate the new hashed password
    hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
    
    # Update the user's password
    user.password = hashed_password
    db.session.commit()
