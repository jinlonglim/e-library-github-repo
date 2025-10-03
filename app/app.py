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

if __name__ == '__main__':
    app.run()

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("shop"))

