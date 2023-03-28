import os
import time
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response




# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///diary.db")




@app.route("/")
@login_required
def index():
    info = db.execute("SELECT * FROM tasks WHERE id = ? AND completed = 'no' ORDER BY due", session["user_id"])
    if not info:
        flash("You currently have no pending tasks!")
    else:
        flash(f"You currently have {len(info)} pending task(s)!")
    return render_template("index.html", info=info)


@app.route("/history")
@login_required
def history():
    info = db.execute("SELECT * FROM tasks WHERE id = ? ORDER BY due DESC", session["user_id"])
    if not info:
        flash("No history found!")
    return render_template("history.html", info=info)

@app.route("/complete")
@login_required
def complete():
    info = db.execute("SELECT * FROM tasks WHERE id = ? AND completed = 'yes' ORDER BY due DESC", session["user_id"])
    flash("Your Completed tasks!")
    return render_template("history.html", info=info)

@app.route("/filter", methods=["GET", "POST"])
@login_required
def filter():
    if request.method == "POST":
        numday = request.form.getlist('days')
        numday = int(numday[0])
        check = request.form.getlist('check')
        done = request.form.getlist('done')
        due = datetime.datetime.today() + datetime.timedelta(days=numday)
        due = due.strftime("%Y-%m-%d")
        start = datetime.datetime.today().strftime("%Y-%m-%d")
        if check and done:
            flash("Please check either none or 1 of the boxes!")
            return redirect("/filter")
        elif check:
            info = db.execute("SELECT * FROM tasks WHERE id = ? AND completed='no' AND due BETWEEN ? and ? ORDER BY due",
                              session["user_id"], start, due)
            if not info:
                flash("No filter results found!")
            return render_template("index.html", info=info)
        elif done:
            info = db.execute("SELECT * FROM tasks WHERE id = ? AND completed='yes' AND due BETWEEN ? and ? ORDER BY due",
                              session["user_id"], start, due)
            if not info:
                flash("No filter results found!")
            return render_template("history.html", info=info)
        else:
            info = db.execute("SELECT * FROM tasks WHERE id = ? AND due BETWEEN ? and ? ORDER BY due",
                              session["user_id"], start, due)
            if not info:
                flash("No filter results found!")
            return render_template("history.html", info=info)
    else:
        return render_template("filter.html")

@app.route("/update", methods=["POST"])
@login_required
def update():
    done = request.form.getlist('check')

    for task in done:
        db.execute("UPDATE tasks SET completed = 'yes', datetime = ? WHERE id = ? AND taskid = ?",
                time.strftime('%Y-%m-%d %H:%M:%S'), session["user_id"], task)

    if done:
        flash("Task list updated!")
    else:
        flash("Please select one or more tasks to update!")
    return redirect("/")

@app.route("/delete", methods=["POST"])
@login_required
def delete():
    done = request.form.getlist('delete')
    for task in done:
        db.execute("DELETE FROM tasks WHERE id = ? AND taskid = ?",
                session["user_id"], task)

    if done:
        flash("Task(s) deleted!")
    else:
        flash("Please select one or more tasks to delete!")
    return redirect("/")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Custom"""
    if request.method == "POST":
        start = request.form.get("start")
        end = request.form.get("end")
        tag = '%' + request.form.get("tag") + '%'
        title = '%' + request.form.get("title") + '%'
        detail = '%' + request.form.get("detail") + '%'
        if start and end:
            if datetime.datetime.strptime(end, '%Y-%m-%d') < datetime.datetime.strptime(start, '%Y-%m-%d'):
                return render_template("apology.html", message="Error: Your end date cannot be before your start date!")
            else:
                info = db.execute("SELECT * FROM tasks WHERE id = ? AND due BETWEEN ? and ? AND title LIKE ? AND detail LIKE ? AND tags LIKE ? ORDER BY due",
                              session["user_id"], start, end, title, detail, tag)
        elif end and not start:
            return render_template("apology.html", message="You need to fill in either both ate fields or only the 'from' field")
        elif start:
            info = db.execute("SELECT * FROM tasks WHERE id = ? AND due BETWEEN ? and ? AND title LIKE ? AND detail LIKE ? AND tags LIKE ? ORDER BY due",
                              session["user_id"], start, start, title, detail, tag)
        else:
            info = db.execute("SELECT * FROM tasks WHERE id = ? AND title LIKE ? AND detail LIKE ? AND tags LIKE ? ORDER BY due",
                              session["user_id"], title, detail, tag)
        if info:
            flash("Your search results")
            return render_template("searched.html", info=info)
        else:
            return render_template("apology.html", message="No search results found.")
    else:
        return render_template("search.html")

@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Custom"""
    if request.method == "POST":
        old = request.form.get("old")
        new = request.form.get("new")
        new2 = request.form.get("new2")
        rows = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])

        if not old or not new or not new2:
            return render_template("apology.html", message="Error, please fill in all the input fields!")
        if new != new2:
            return render_template("apology.html", message="Error, your new passwords do not match!")

        # Ensure username exists and password is correct
        if check_password_hash(rows[0]["hash"], old):
            db.execute("UPDATE users SET hash = ? WHERE id = ? ",
                       generate_password_hash(new, "sha256", 8), session["user_id"])
            flash("New password saved!")
            return redirect("/")
        else:
            return render_template("apology.html", message="Error: Incorrect Password")
    else:
        return render_template("password.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", message="Error: Please fill in your username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", message="Error: Please fill in your password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("apology.html", message="Invalid username or password!")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        flash("Welcome to your Task List!")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        title = request.form.get("title")
        if not title:
            return render_template("apology.html", message="Please fill in the title of your task")
        date = request.form.get("date")
        if not date:
            return render_template("apology.html", message="Please fill in the due date of your task")
        details = request.form.get("details")
        if not details:
            return render_template("apology.html", message="Please fill in the details of your task")
        tags = request.form.get("tags")
        if not tags:
            return render_template("apology.html", message="Please fill in the tags of your task")
        db.execute("INSERT INTO tasks (id, title, detail, due, tags) VALUES (?, ?, ?, ?, ?)",
                   session["user_id"], title, details, date, tags)
        flash("Task entered!")
        return render_template("new.html")
    else:
        return render_template("new.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()
    if request.method == "POST":
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        username = request.form.get("username")

        if not username or not password or not confirmation:
            return render_template("apology.html", message="Error, please fill in all the input fields!")

        if password != confirmation:
            return render_template("apology.html", message="Error, passwords do not match")

        users = db.execute("SELECT * FROM users WHERE username=?", username)

        if users:
            return render_template("apology.html", message="Error, username already in use, please register using a different username")
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password, "sha256", 8))
        flash("Account created!")
        return redirect("/")

    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
