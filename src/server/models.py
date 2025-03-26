from . import db  # Import db instance from your main app file
import datetime
from werkzeug.security import generate_password_hash, check_password_hash  # Import hashing functions
from flask_login import UserMixin  # Import UserMixin


# Modify the User class to include UserMixin and password methods
class User(UserMixin, db.Model):  # Add UserMixin here
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))  # Increased length for potentially longer hashes
    email = db.Column(db.String(120), unique=True, nullable=True)
    nickname = db.Column(db.String(80), nullable=True)
    role = db.Column(db.String(20), default='USER')
    created_ts = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_ts = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    memos = db.relationship('Memo', backref='creator', lazy=True)
    resources = db.relationship('Resource', backref='creator', lazy='dynamic')

    def set_password(self, password):
        """Create hashed password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Memo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_ts = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    updated_ts = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    # Foreign Key to link Memo to its creator (User)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    visibility = db.Column(db.String(20), default='PRIVATE')  # e.g., PRIVATE, PROTECTED, PUBLIC
    resources = db.relationship('Resource', backref='memo', lazy='dynamic',
                                cascade="all, delete-orphan")  # Added relationship and cascade
    # Add other fields like pinned, row_status (NORMAL, ARCHIVED) etc.
    # payload = db.Column(db.Text) # For storing JSON data like tags?

    def __repr__(self):
        return f'<Memo {self.id}>'

# --- Add Resource Model ---
class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_ts = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_ts = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    filename = db.Column(db.String(255), nullable=False) # Original filename
    internal_filename = db.Column(db.String(255), nullable=False, unique=True) # Unique filename used for storage
    # internal_path = db.Column(db.String(255), nullable=False) # Maybe store just filename and build path?
    external_link = db.Column(db.String(1024), nullable=True) # For URL resources later
    type = db.Column(db.String(128), nullable=False) # MIME type
    size = db.Column(db.Integer, nullable=False) # Size in bytes
    # Foreign Key to link Resource to its Memo
    memo_id = db.Column(db.Integer, db.ForeignKey('memo.id'), nullable=True) # Nullable if resource can exist before memo

    def __repr__(self):
        return f'<Resource {self.filename}>'
