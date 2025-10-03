from flask import Flask, app
from flask_mongoengine import MongoEngine
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '49c02eb67b7b2c75412ed8cb13a3ffa7'  # Replace with a secure key in production

    # Initialize MongoDB
    app.config['MONGODB_SETTINGS'] = {
        'db': 'sg_library_db',
        'host': 'localhost',
        'port': 27017
    }
    db = MongoEngine(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'  # Redirect to login page if unauthenticated or unauthorized
    return app, db, login_manager

# Initialize the app and db instances
app, db, login_manager = create_app()