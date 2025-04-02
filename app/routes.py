from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

# Create blueprint
main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    """Render the home page"""
    return render_template('index.html', title='Home')

@main.route('/dashboard')
@login_required
def dashboard():
    """Render the dashboard page (requires login)"""
    return render_template('dashboard.html', title='Dashboard')
