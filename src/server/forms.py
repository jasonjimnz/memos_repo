from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.simple import TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from .models import User  # Import User model to check if username/email exists


class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """Check if username already exists."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        """Check if email already exists."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one or login.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class MemoForm(FlaskForm):
    content = TextAreaField('Memo Content', validators=[DataRequired(), Length(max=10000)])  # Basic content field
    resource_files = MultipleFileField('Attach Files', validators=[  # Renamed field for clarity
        FileAllowed([
            'jpg', 'jpeg', 'png', 'gif', 'pdf', 'txt', 'md',
            'doc', 'docx', 'xls', 'xlsx', 'zip', 'gitignore',
            'Dockerfile', 'yml', 'yaml', 'csv', 'gz'
        ],
            'Allowed file types only!'),
        # FileSize doesn't directly apply to MultipleFileField; check size in the route logic.
    ])
    # Add visibility options later if needed (e.g., SelectField)
    submit = SubmitField('Save Memo')
