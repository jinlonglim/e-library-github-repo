from flask import Flask, render_template, flash, request, session, redirect, url_for
from app.model import LoginForm, RegForm, Book, User
from app import app
from flask_login import login_user, logout_user, login_required, current_user
import csv
import io
from .books import all_books


@app.route('/')
#@app.route('/home')
def home():
    category = request.args.get('category', "All")
    if category == "All":
        books = all_books
    else:
        books = [book for book in all_books if book['category'] == category]
        
    # sort alphabetically by title
    books = sorted(books, key=lambda x: x['title'])
    return render_template('home.html', books=books, category=category)

    
@app.route('/details/<title>')
def details(title):
    # find book by title
    book = next((book for book in all_books if book['title'] == title), None)
    return render_template('details.html', book=book)



@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# create a route for login page
@app.route("/login", methods=["GET", "POST"])
#function for login
def login():
    form = LoginForm()
    #display the login form
    if request.method == "GET":
        return render_template("login.html", form=form)
    else:
        #process the login form
        email = request.form["email"]
        password = request.form["password"]
        user = User.get_user_credentials(email, password) #check if valid user
        if user:
            login_user(user, remember=form.remember_me.data)  #login the user
            flash("Login successful!", "success")
            return redirect(url_for("home")) #redirect to function home after login
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for("login")) #redirect to function login
        
# create route for registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegForm()
    if request.method == "GET":
        
        return render_template("register.html", form=form)
    elif form.validate_on_submit():
        # process the registration form
        name = request.form["name"]
        password = request.form["password"]
        email = request.form["email"]
        # For simplicity, we are not storing the user in a database
        if User.create_user(name=name, email=email, password_hash=password):
            flash("Registration successful. Please log in.", "success")
        else:
            flash("Registration failed. User may already exist.", "danger")
        return redirect(url_for("login")) #redirect to function login after registration
    return render_template("register.html", form=form)


if __name__ == '__main__':
    app.run()