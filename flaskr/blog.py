from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("blog", __name__)

@bp.route("/")
def index():
    """Show all the blog posts."""
    # Gets database connection
    db = get_db()
    # Runs SQL query to select all blog posts, joining each post with the author's
    # username, and orders them by creation first
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    # renders the index template and passes the lists of posts to it for display
    return render_template("blog/index.html", posts=posts)

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new blog post."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        # checks if title field is empty and updates error message to be flashed
        if not title:
            error = "Title is required."

        if error is not None:
            # prints error to screen if one exists 
            flash(error)
        else:
            db = get_db()
            # inserts users title, body, and gets user id to insert into the post table in the database
            db.execute(
                "INSERT INTO post (title, body, author_id)"
                "VALUES (?, ?, ?)", (title, body, g.user['id'])
            )
            db.commit() # saves changes to the database
            return redirect(url_for("blog.index")) # redirects the user to the blog index page once db changes committed
    return render_template("blog/create.html") # On first use and if error, renders the create blog page

def get_post(id, check_author=True):
    """Returns post of user by passed in id"""
    post = get_db().execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE p.id = ?", 
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} does not exist.")
    
    if check_author and post["author_id"] != g.user["id"]:
        abort(403)
    
    return post

@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """view function to update the user's post in the database"""
    post = get_post(id)

    # used to save post request details to variables to use in the SQL script
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        # checks to make sure a title has been provided and returns an error if not
        if not title:
            error = "Title is required."

        # Flashes error if one exists outside of no title which is handled above
        if error is not None:
            flash(error)
        else:
            db = get_db()
            # Updates post in the database with user's changes"
            db.execute(
                "UPDATE post SET title = ?, body = ?"
                " WHERE id = ?",
                (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))
    
    return render_template("blog/update.html", post=post)

@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Deletes post from database"""
    get_post(id)
    db = get_db()
    db.execute(
        "DELETE FROM post WHERE id = ?",
        (id,)
    )
    db.commit()
    return redirect(url_for("blog.index"))