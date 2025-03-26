from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager # Import LoginManager
import os
from dotenv import load_dotenv
import markdown
import bleach
from markupsafe import Markup

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager() # Initialize LoginManager
login_manager.login_view = 'auth.login' # Tell Flask-Login which route handles login
login_manager.login_message_category = 'info' # Optional: category for flashed messages

@login_manager.user_loader
def load_user(user_id):
    """User loader callback used by Flask-Login."""
    from .models import User # Import User model here
    return User.query.get(int(user_id))

def markdown_to_html(text):
    # ... (keep the existing function code) ...
    allowed_tags = [
        'p', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'br', 'a', 'blockquote',
        'pre', 'code', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img',
    ]
    allowed_attrs = {
        '*': ['class'],
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
    }
    html = markdown.markdown(text, extensions=['fenced_code', 'tables', 'nl2br'])
    safe_html = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)
    # The Markup object is now correctly imported from markupsafe
    return Markup(safe_html)

def create_app():
    app = Flask(__name__, instance_relative_config=False)

    upload_folder_path = os.path.join(app.instance_path, 'uploads')
    app.config['UPLOAD_FOLDER'] = upload_folder_path
    # Create the folder if it doesn't exist
    os.makedirs(upload_folder_path, exist_ok=True)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-default-fallback-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.jinja_env.filters['markdown'] = markdown_to_html

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app) # Initialize LoginManager with the app

    with app.app_context():

        # Register Main Blueprint
        from . import main_routes
        app.register_blueprint(main_routes.bp)

        # Register Auth Blueprint (We'll create auth_routes.py next)
        from . import auth_routes
        app.register_blueprint(auth_routes.bp, url_prefix='/auth') # Add URL prefix for auth routes

        return app