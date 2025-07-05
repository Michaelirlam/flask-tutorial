import functools
from flask import (
    Blueprint, flash, g, redirect,  render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")

# Associates URL /register with the below register view function
@bp.route("/register", methods=("GET", "POST"))
def register():
    # if method is POST, start validating the input
    if register.method == "POST":
        # request.form is a special type of dict mapping submitted form keys and values
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        # Checks if username or password are left empty by the user
        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        # If username and password are filled in, tries to execute the request
        if error is None:
            try:
                # tries to enter username and password into the user DB. Hashes password for security
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                # Commit needed to save changes to the modified data
                db.commit()
            except db.IntegrityError:
                # Catches if username already exists in the database as this needs to be unique
                error = f"User {username} is already registered."
            else:
                # Following successful execution, redirects user to login screen
                return redirect(url_for("auth.login"))
        
        flash(error)
    
    # returns the registration template if user is accessing for first time or if there is an error
    return render_template("auth/register.html")

@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        # User queried and stored in variable "user"
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone() # returns one row from the query. If the query returned no results, it returns None.

        if user is None:
            error = "Incorrect username."
        # hashes the submitted password in the same way as the stored hash and securely compares them. If they match, the password is valid. 
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."
        
        if error is None:
            # session is a dict that stores data across requests
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))
        
        flash(error)

        # When validation succeeds, the user’s id is stored in a new session. The data is stored in a cookie that is sent to the browser, 
        # and the browser then sends it back with subsequent requests. Flask securely signs the data so that it can’t be tampered with.
    
    # returns the login template if user is accessing for first time or if there is an error
    return render_template("auth/login.html")

bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g,user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id)
        ).fetchone