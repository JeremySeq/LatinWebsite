from flask import Blueprint, jsonify, request, current_app
import jwt
import datetime
import db
import login

login_routes = Blueprint('login_routes', __name__)

@login_routes.route("/", methods=["POST"])
def login_user():
    username = request.form.get('username')
    password = request.form.get('password')
    user = login.login_user(username, password)

    if user:
        token = jwt.encode({"user": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)}, current_app.config["SECRET_KEY"])
        print("Logged in user: " + user.username)
        return jsonify({"message": "Logged in", "token": token}), 200

    return jsonify({"message": "Incorrect username and password"}), 401

@login_routes.route("/register", methods=["POST"])
def register_user():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get("email")

    if not username or not password or not email:
        return jsonify({"message": "Missing username, password, or email."}), 400
    
    register_bool = login.register_user(username, email, password)

    if register_bool:
        return jsonify({"message": "Registered user successfully"}), 200
    
    return jsonify({"message": "Registration failed."}), 200
