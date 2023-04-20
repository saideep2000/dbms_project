from flask import Flask, render_template, request, redirect, url_for, Blueprint
from db import db
from model import UserModel
from flask import session
login_bp = Blueprint("login_bp", __name__)


@login_bp.route("/login", methods=["POST"])
def login():
    # username = request.form["username"]
    # password = request.form["password"]
    # TODO: revert to above
    username = "johndoe"
    password = "password123"
    with db.cursor() as cursor:
        # query the database for the username and password
        query = "SELECT * FROM NUser WHERE username=%s AND upassword=%s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            session["user_id"] = user.get("id")
            session["first_name"] = user.get("first_name")
            session["last_name"] = user.get("last_name")
            session["username"] = username
            return redirect(url_for("events_bp.events"))
        else:
            return redirect(url_for("index_bp.index"))