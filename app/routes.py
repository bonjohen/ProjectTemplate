from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import cache
from app.models import Page, User

# Create blueprint
main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@cache.cached(timeout=60)  # Cache for 1 minute
def index():
    """Render the home page"""
    # Get the latest published pages
    recent_pages = Page.query.filter_by(is_published=True).order_by(Page.published_at.desc()).limit(3).all()
    return render_template('index.html', title='Home', recent_pages=recent_pages)

@main.route('/dashboard')
@login_required
def dashboard():
    """Render the dashboard page (requires login)"""
    return render_template('dashboard.html', title='Dashboard')

@main.route('/api-docs')
@cache.cached(timeout=3600)  # Cache for 1 hour
def api_docs():
    """Render the API documentation page"""
    return render_template('api_docs.html', title='API Documentation')

@main.route('/sitemap')
@cache.cached(timeout=300)  # Cache for 5 minutes
def sitemap():
    """Generate a simple sitemap of all pages"""
    pages = Page.query.filter_by(is_published=True).all()
    return render_template('sitemap.html', title='Sitemap', pages=pages)
