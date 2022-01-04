# Implementation inspired from CS50 Finance Assignment

import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

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

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///personalFinances.db")


# add_cash method: adds money to user account given an amount
@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    if request.method == "POST":
        amount = request.form.get("cash")
        
        # update cash value in users table
        db.execute("""
            UPDATE users
            SET cash = cash + :amount
            WHERE id=:user_id
        """, amount = amount,
        user_id = session["user_id"])
        
        # add a transaction to transactions table
        db.execute("""
            INSERT INTO transactions (user_id, symbol, shares)
            VALUES (:user_id, :symbol, :shares)
            """,
            user_id=session["user_id"],
            symbol = "Income",
            shares = amount
        )
        
        flash("Added Money to Account!")
        return redirect("/history")
    else:
        return render_template("add_cash.html")


# buy method: adds a transaction to the user account (subtracting from balance)
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Add transaction"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = float(request.form.get("shares")) * -1
        
        # get cash from users table for this user
        rows = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])
        cash = rows[0]["cash"]
        updated_cash = cash + shares
        
        # update cash with updated cash value for this user
        db.execute("UPDATE users SET cash=:updated_cash WHERE id=:id",
                    updated_cash=updated_cash,
                    id=session["user_id"])
                    
        # add new transaction into transactions table for this user
        db.execute("""
            INSERT INTO transactions (user_id, symbol, shares)
            VALUES (:user_id, :symbol, :shares)
            """,
            user_id=session["user_id"],
            symbol = symbol,
            shares = shares,
        )
        flash("Transaction Added!")
        return redirect("/history")

    else:
        return render_template("buy.html")


# history method: displays all transactions for user
@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    
    # get all transactions for this user from the transactions table
    transactions = db.execute("""
        SELECT symbol, shares, transacted
        FROM transactions
        WHERE user_id=:user_id
    """, user_id=session["user_id"])
    rows = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])
    cash = rows[0]["cash"]
    cash1 = round(cash, 2)

    return render_template("history.html", transactions=transactions, cash1=cash1)

# is_provided method: returns apology if a field is not provided
def is_provided(field):
    if not request.form.get(field):
        return apology(f"must provide {field}", 403)


# register method: allows a user to create a new account
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        result_checks = is_provided("username") or is_provided("password") or is_provided("confirmation")
        if result_checks != None:
            return result_checks
        if request.form.get("password") != request.form.get("confirmation"):
            return redirect("/register1")
            
        # Add new user to users database
        try:
            prim_key = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                    username=request.form.get("username"),
                    hash=generate_password_hash(request.form.get("password")))
        except:
            return redirect("/register2")
        if prim_key is None:
            return redirect("/register1")
        session["user_id"] = prim_key
        flash("Registered!")
        return redirect("/history")
    else:
        return render_template("register.html")


# register1 method: register page when registration fails due to passwords not matching
@app.route("/register1", methods=["GET", "POST"])
def register1():
    flash("Passwords don't match!")
    if request.method == "POST":
        result_checks = is_provided("username") or is_provided("password") or is_provided("confirmation")
        if result_checks != None:
            return result_checks
        if request.form.get("password") != request.form.get("confirmation"):
            return redirect("/register1")
        
        # Add new user to users database
        try:
            prim_key = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                    username=request.form.get("username"),
                    hash=generate_password_hash(request.form.get("password")))
        except:
            return redirect("/register2")
        if prim_key is None:
            return redirect("/register1")
        session["user_id"] = prim_key
        flash("Registered!")
        return redirect("/history")
    else:
        return render_template("register.html")


# register2 method: register page when registration fails due to username already existing
@app.route("/register2", methods=["GET", "POST"])
def register2():
    flash("Username already exists!")
    if request.method == "POST":
        result_checks = is_provided("username") or is_provided("password") or is_provided("confirmation")
        if result_checks != None:
            return result_checks
        if request.form.get("password") != request.form.get("confirmation"):
            return redirect("/register1")
                
        # Add new user to users database
        try:
            prim_key = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                    username=request.form.get("username"),
                    hash=generate_password_hash(request.form.get("password")))
        except:
            return redirect("/register2")
        if prim_key is None:
            return redirect("/register1")
        session["user_id"] = prim_key
        flash("Registered!")
        return redirect("/history")
    else:
        return render_template("register.html")


# login method: user can enter credentials to log in
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username and password was submitted
        result_checks = is_provided("username") or is_provided("password")
        if result_checks is not None:
            return result_checks


        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return redirect("/login1")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to index page
        return redirect("/history")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# login1 method: login page when incorrect username or password is entered
@app.route("/login1", methods=["GET", "POST"])
def login1():
    """Log user in"""

    # Forget any user_id
    session.clear()

    flash("Incorrect Username or Password!")
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username and password was submitted
        result_checks = is_provided("username") or is_provided("password")
        if result_checks is not None:
            return result_checks


        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return redirect("/login1")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to index page
        return redirect("/history")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# logout method: allows a user to log out by clearing the session
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("You have successfully logged out")
    return redirect("/login")


# errorhandler method: returns apology page with error code
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors (polling)
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
