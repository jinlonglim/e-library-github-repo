from flask import Flask, render_template, flash, request, session, redirect, url_for
from app.model import LoginForm, RegForm, Book, User, AddBookForm, Loan
from datetime import datetime
from app import app, db, login_manager
from flask_login import login_user, logout_user, login_required, current_user

# from .books import all_books

# # Insert all books from books.py into MongoDB if not already present
# Book.init_books(all_books)


@app.route('/')
def home():
    category = request.args.get('category', "All")
    if category == "All":
        books = Book.get_all_books().order_by('title')
    else:
        books = Book.objects(category=category).order_by('title')

    return render_template('home.html', books=books, category=category)


@app.route('/details/<title>')
def details(title):
    # find book by title
    book = Book.objects(title=title).first()
    return render_template('details.html', book=book)

#add_book route for admin user
@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if current_user.email != 'admin@lib.sg':
        flash("Access denied. Admin only.", "danger")
        return redirect(url_for('home'))
    
    form = AddBookForm()
    if form.validate_on_submit():
        #collect authors from the form
        authors = []
        
        author1 = form.author.data.strip()
        if form.illustrator1.data:
            author1 += " (Illustrator)"
        authors.append(author1)
        
        # author2-5 are optional
        for i in range(2, 6):
            author_field = getattr(form, f'author{i}')
            illustrator_field = getattr(form, f'illustrator{i}')
            
            if author_field.data and author_field.data.strip():
                author_name = author_field.data.strip()
                if illustrator_field.data:
                    author_name += " (Illustrator)"
                authors.append(author_name)
        
        book = Book(
            title=form.title.data,
            authors=authors,
            category=form.category.data,
            description=[form.description.data],
            url=form.url.data,
            pages=form.pages.data,
            copies=form.copies.data,
            available=form.copies.data,
            genres=form.genres.data
        )
        book.save()
        flash("Book added successfully!", "success")
        #remain on the add_book page after adding a book
        return redirect(url_for('add_book'))
    return render_template('add_book.html', form=form)


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