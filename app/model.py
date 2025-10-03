from datetime import datetime, timedelta
import random
from flask_wtf import FlaskForm
from flask_login import UserMixin
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectMultipleField, SelectField,TextAreaField
from wtforms.validators import DataRequired, Email, Length
from app import db, login_manager

class LoginForm(FlaskForm):
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
    submit = SubmitField('Register')
# addbook form to add new book to db
genres = ["Animals", "Business", "Comics", "Communication", "Dark Academia", 
"Emotion", "Fantasy", "Fiction", "Friendship", "Graphic Novels", "Grief", 
"Historical Fiction", "Indigenous", "Inspirational", "Magic", "Mental Health", 
"Nonfiction", "Personal Development",  "Philosophy", "Picture Books", "Poetry", 
"Productivity", "Psychology", "Romance", "School", "Self Help"] 
categories = ["Children", "Teens", "Adult"]

class AddBookForm(FlaskForm):
    title = StringField(
        'Title',
        validators=[DataRequired(message="Title is required.")]
    )
    author = StringField(
        'Author',
        validators=[DataRequired(message="Author is required.")]
    )
    author2 = StringField('Author 2 (optional)')
    author3 = StringField('Author 3 (optional)')
    author4 = StringField('Author 4 (optional)')
    author5 = StringField('Author 5 (optional)')
    
    illustrator1 = BooleanField('Illustrator')
    illustrator2 = BooleanField('Illustrator')
    illustrator3 = BooleanField('Illustrator')
    illustrator4 = BooleanField('Illustrator')
    illustrator5 = BooleanField('Illustrator')
    
    category = SelectField(
        'Category',
        choices=[(category, category) for category in categories],
        validators=[DataRequired(message="Category is required.")]
    )
    genres = SelectMultipleField(
        'Genres',
        choices=[(genre, genre) for genre in genres],
        validators=[DataRequired(message="Please select at least one genre.")]
    )
    url = StringField(
        'URL',
        validators=[DataRequired(message="URL is required.")]
    )
    description = TextAreaField(
        'Description',
        validators=[DataRequired(message="Description is required.")]
    )
    pages = IntegerField(
        'Pages',
        validators=[DataRequired(message="Pages are required.")]
    )
    copies = IntegerField(
        'Copies',
        validators=[DataRequired(message="Copies are required.")]
    )
    submit = SubmitField('Add Book')

class Book(db.Document):
    
    # Meta class for model configuration
    meta = {
        'collection': 'books',
        'ordering': ['title'] #descending order
    }
    title = db.StringField(
        max_length=200, 
        required=True,
    )
    authors = db.ListField(
        db.StringField(max_length=100),
        required=True,
    )
    category = db.StringField(
        max_length=50,
        required=True,
    )
    genres = db.ListField(
        db.StringField(max_length=50),
    )
    copies = db.IntField(
        required=True,
        min_value=0,
        default=0,
    )
    available = db.IntField(
        required=True,
        min_value=0,
        default=0,
    )
    url = db.StringField(
        max_length=255,
    )
    description = db.ListField(
        db.StringField(),
    )
    pages = db.IntField(
        min_value=1,
    )

    def loan_book(self):
        if self.available > 0:
            self.available -= 1
            self.save()
            return True
        return False
    
    def return_book(self):
        if self.available < self.copies:
            self.available += 1
            self.save()
            return True
        return False
    #static method has access to nothing so no need define instance, self
    #can just call class name directly

    @staticmethod
    def get_all_books():
        return Book.objects()
    
    @staticmethod
    #use this method to initialize the db with books from books.py
    def init_books(all_books):
        #if no books in db, add all from books.py
        if Book.objects.count() == 0:
            for book_data in all_books:
                # Check if book already exists by title
                if not Book.objects(title=book_data['title']).first():
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
                    
      
class User(db.Document, UserMixin):
    meta = {
        'collection': 'users'
    }

    name = db.StringField(
        max_length=150,
        required=True,
        unique=True
    )
    email = db.StringField(
        max_length=255,
        required=True,
        unique=True
    )
    password_hash = db.StringField(
        required=True
    )
    def get_id(self):
        return self.email
    
    @staticmethod
    def get_user_by_name(name):
        return User.objects(name=name).first()
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
    def get_user_credentials(email, password_hash):
        user = User.get_user_by_email(email)
        if user and user.password_hash == password_hash:
            return user
        return None
              
class Loan(db.Document):
    meta = {
        'collection': 'loans',
    }
    member = db.ReferenceField(User, required=True)
    book = db.ReferenceField(Book, required=True)
    borrow_date = db.DateTimeField(required=True)
    return_date = db.DateTimeField()
    due_date = db.DateTimeField(required=True)
    renew_count = db.IntField(default=0)
    
    @staticmethod
    def create_loan(member, book):
        # Check if member already has unreturned loan for this book
        existing = Loan.objects(member=member, book=book, return_date=None).first()
        if existing:
            return None
        
        if book.available > 0:
            # Generate random borrow date 10-20 days before today
            days_ago = random.randint(10, 20)
            borrow_date = datetime.now() - timedelta(days=days_ago)
            due_date = borrow_date + timedelta(days=14)

            loan = Loan(member=member, book=book, borrow_date=borrow_date, due_date=due_date)
            loan.save()
            book.loan_book()
            return loan
        return None
    
    @staticmethod
    def get_user_loans(member):
        return Loan.objects(member=member).order_by('-borrow_date')

    @staticmethod
    def get_loan_by_id(loan_id):
        return Loan.objects(id=loan_id).first()
    
    def renew_loan(self):
        if self.renew_count < 2 and not self.is_overdue():
            # Generate new borrow date 10-20 days after current
            days_forward = random.randint(10, 20)
            new_borrow_date = self.borrow_date + timedelta(days=days_forward)
            
            # Cannot be later than today
            if new_borrow_date > datetime.now():
                new_borrow_date = datetime.now()
            
            self.borrow_date = new_borrow_date
            self.due_date = new_borrow_date + timedelta(days=14)
            self.renew_count += 1
            self.save()
            return True
        return False
    
    def return_loan(self):
        if not self.return_date:
            # Generate return date 10-20 days after borrow date
            days_forward = random.randint(10, 20)
            return_date = self.borrow_date + timedelta(days=days_forward)
            
            # Cannot be later than today
            if return_date > datetime.now():
                return_date = datetime.now()
            
            self.return_date = return_date
            self.save()
            self.book.return_book()
            return True
        return False
    
    def delete_loan(self):
        if self.return_date:
            self.delete()
            return True
        return False
    
    def is_overdue(self):
        return datetime.now() > self.due_date and not self.return_date
    
    def can_renew(self):
        return self.renew_count < 2 and not self.is_overdue() and not self.return_date
    
    def can_return(self):
        return not self.return_date


#used by flask-login to reload the user object from the user stored in the session
#check if valid user, if valid return user object
@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_email(user_id)