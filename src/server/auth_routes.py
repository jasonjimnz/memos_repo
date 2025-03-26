from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from . import db
from .models import User
from .forms import LoginForm, SignupForm

# Create Auth Blueprint
bp = Blueprint('auth', __name__)


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # Redirect if already logged in
    form = SignupForm()
    if form.validate_on_submit():
        # Check if host user already exists (assuming first user is host)
        # This logic might need refinement based on Memos' actual setup process
        role = 'ADMIN' if not User.query.first() else 'USER'
        user = User(username=form.username.data, email=form.email.data, role=role)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('signup.html', title='Sign Up', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # Redirect if already logged in
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        # Log the user in
        login_user(user, remember=form.remember_me.data)
        flash(f'Welcome back, {user.username}!', 'success')
        # Redirect to the page the user was trying to access, or index
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))
    return render_template('login.html', title='Login', form=form)


@bp.route('/logout')
@login_required  # Ensure user is logged in before logging out
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
