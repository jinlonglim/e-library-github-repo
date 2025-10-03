from flask_wtf import FlaskForm
from flask_login import UserMixin
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app import db, login_manager

class LoginForm(FlaskForm):
    """
    Represents a login form for a web application.

    This form includes fields for username, password, and a "remember me" checkbox.
    It uses Flask-WTF to handle form validation and rendering.
    """
    email = StringField(
        'email',
        validators=[DataRequired(message="Email is required."), Email(message="Invalid email address.")]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message="Password is required.")]
    )
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')
    

class RegForm(FlaskForm):
    """
    Represents a registration form for a new user.

    This form includes fields for username, email, password, and a password confirmation.
    It uses Flask-WTF to handle form validation.
    """
    name = StringField(
        'name',
        validators=[DataRequired(message="Name is required.")]
    )
    email = StringField(
        'email',
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Invalid email address.")
        ]
    )
    password = PasswordField(
        'password',
        validators=[
            DataRequired(message="Password is required."),
            Length(min=5, message="Password must be at least 5 characters long.")
        ]
    )
    # confirm_password = PasswordField(
    #     'confirm password',
    #     validators=[
    #         DataRequired(message="Please confirm your password."),
    #         EqualTo('password', message="Passwords do not match.")
    #     ]
    # )
    submit = SubmitField('Register')

from flask_mongoengine import MongoEngine
from decimal import Decimal

# Initialize the Flask-MongoEngine extension. 
# In a real application, you would do this in your main app file.
# For this example, we'll assume a 'db' instance is available.
# db = MongoEngine()

class Book(db.Document):
    """
    A model to represent an item in an e-commerce inventory.
    
    This model stores key details about a product, including its identifier,
    name, description, stock quantity, and price.
    """
    
    # Meta class for model configuration
    meta = {
        'collection': 'books',
        'ordering': ['title']
    }
    title = db.StringField(
        max_length=200, 
        required=True,
        help_text="The title of the book."
    )
    authors = db.ListField(
        db.StringField(max_length=100),
        required=True,
        help_text="A list of authors for the book."
    )
    category = db.StringField(
        max_length=50,
        required=True,
        help_text="The category or genre of the book."
    )
    genres = db.ListField(
        db.StringField(max_length=50),
        help_text="A list of genres associated with the book."
    )
    copies = db.IntField(
        required=True,
        min_value=0,
        default=0,
        help_text="The number of copies available for the book."
    )
    available = db.IntField(
        required=True,
        min_value=0,
        default=0,
        help_text="The number of copies currently available for the book."
    )
    url = db.StringField(
        max_length=255,
        help_text="A URL to an image or webpage for the book."
    )
    description = db.ListField(
        db.StringField(),
        help_text="A list of descriptions for the book."
    )
    pages = db.IntField(
        min_value=1,
        help_text="The number of pages in the book."
    )

    #static method has access to nothing so no need define instance, self
    #can just call class name directly
    @staticmethod
    def get_books_by_id(book_id):
        return Book.objects(book_id=book_id).first()

    @staticmethod
    def get_all_books():
        return Book.objects()
    
    @staticmethod
    def init_books(all_books):
        #if no books in db, add all from books.py
        if Book.objects.count() == 0:
            for book_data in all_books:
                # Check if book already exists by title
                if not Book.objects(title=book_data['title']).first():
                    # Convert authors list to string if needed
                    authors = ", ".join(book_data['authors']) if isinstance(book_data.get('authors'), list) else book_data.get('authors', '')
                    # Create and save the book
                    Book(
                        title=book_data['title'],
                        authors=book_data.get('authors', []),
                        category=book_data.get('category', ''),
                        genres=book_data.get('genres', []),
                        copies=book_data.get('copies', 0),
                        available=book_data.get('available', 0),
                        url=book_data.get('url', ''),
                        description=book_data.get('description', []),
                        pages=book_data.get('pages', 0)
                    ).save()
                    #do i need to return anything?

#user class
class User(db.Document, UserMixin):
    """
    A model to represent a user in the application.

    This model stores user credentials and profile information.
    """
    
    meta = {
        'collection': 'users'
    }

    name = db.StringField(
        max_length=150,
        required=True,
        unique=True,
        help_text="The user's unique name."
    )
    email = db.StringField(
        max_length=255,
        required=True,
        unique=True,
        help_text="The user's email address."
    )
    password_hash = db.StringField(
        required=True,
        help_text="A hashed version of the user's password."
    )
    
    @staticmethod
    def get_user_by_email(email):
        return User.objects(email=email).first()
    
    @staticmethod
    def create_user(name, email, password_hash):
        user = User(
            name=name,
            email=email,
            password_hash=password_hash
        )
        user.save()
        return user
    
    @staticmethod
    def get_user_by_id(user_id):
        return User.objects(id=user_id).first()
    
    @staticmethod
    def get_user_credentials(email, password_hash):
        user = User.get_user_by_email(email)
        if user and user.password_hash == password_hash:
            return user
        return None
    
    @staticmethod
    def save_user(name, email, password_hash):
        user = User(name=name, email=email, password_hash=password_hash)
        user.save()
        return user

#used by flask-login to reload the user object from the user ID stored in the session
#check if valid user, if valid return user object
@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(user_id)