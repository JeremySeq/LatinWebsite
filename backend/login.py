import db
import jwt
from flask import current_app, request, jsonify
from functools import wraps

def requires_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = getUserFromRequest(request)
        if user is None:
            return jsonify({"message": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated

def getUserFromRequest(request):
    token = request.headers.get('Authorization') or request.form.get('Authorization') or request.args.get("Authorization")

    if not token:
        return None
    data = None
    try:
        token = token.removeprefix('Bearer ')
        data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms="HS256")
        username = data["user"]
        return db.User.query.filter_by(username=username).first()
    except:
        return None


def register_user(username, email, password):
    # TODO: make this function give back a message along with the
    # boolean, saying for example, why the registration failed.

    # check if user already registered with this username
    unique = db.User.query.filter_by(username=username).first()
    if unique is not None:
        return False
    
    # check if user already registered with this email address
    unique = db.User.query.filter_by(email=email).first()
    if unique is not None:
        return False

    # hash the password and create the new user
    hashed_password = hash_password(password)
    new_user = db.User(username=username, email=email, password_hash=hashed_password)
    db.db.session.add(new_user)
    db.db.session.commit()

    return True

def login_user(username, password):

    # get user with given username
    user = db.User.query.filter_by(username=username).first()

    # if user doesn't exist, return False
    if user is None:
        return False
    
    # hash the given password and check if it matches the one in the database
    hashed_password = hash_password(password)
    if user.password_hash != hashed_password:
        return False
    
    return user

def hash_password(password):
    return password # TODO: hash the password here
