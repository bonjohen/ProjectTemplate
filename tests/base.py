"""
Base test class for the application.
"""
import unittest
from flask import url_for
from flask_login import login_user, current_user
from app import create_app, db
from app.models import User, Page, Tag
from config import Config
from datetime import datetime, timezone
import base64

class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # Use in-memory database for testing
    WTF_CSRF_ENABLED = False  # Disable CSRF protection for testing
    SECRET_KEY = 'test-secret-key'

class BaseTestCase(unittest.TestCase):
    """Base test case for the application"""

    def setUp(self):
        """Set up test environment"""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Create test data
        self.setup_test_data()

    def tearDown(self):
        """Tear down test environment"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def setup_test_data(self):
        """Set up test data"""
        # Create test user
        self.user = User(
            username='testuser',
            email='test@example.com',
            role='admin',  # Use admin role for testing
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        self.user.set_password('password')
        db.session.add(self.user)

        # Create test tag
        self.tag = Tag(name='TestTag')
        db.session.add(self.tag)

        db.session.commit()

    def login(self, email='test@example.com', password='password'):
        """Log in a user for testing"""
        with self.client.session_transaction() as sess:
            # Get the user
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                # Set up the session as if the user is logged in
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
                return True
        return False

    def logout(self):
        """Log out a user for testing"""
        with self.client.session_transaction() as sess:
            if '_user_id' in sess:
                del sess['_user_id']
            if '_fresh' in sess:
                del sess['_fresh']

    def create_page(self, title='Test Page', slug='test-page', content='Test content', is_published=True):
        """Create a test page"""
        # Make sure we're logged in
        self.login()

        return self.client.post(
            '/content/page/new',
            data={
                'title': title,
                'slug': slug,
                'content': content,
                'summary': 'Test summary',
                'is_published': is_published,
                'tags': [self.tag.id]
            },
            follow_redirects=True
        )

    def edit_page(self, slug, new_title='Updated Title', new_slug='updated-slug'):
        """Edit a test page"""
        # Make sure we're logged in
        self.login()

        return self.client.post(
            f'/content/page/{slug}/edit',
            data={
                'title': new_title,
                'slug': new_slug,
                'content': 'Updated content',
                'summary': 'Updated summary',
                'is_published': True,
                'tags': [self.tag.id]
            },
            follow_redirects=True
        )

    def delete_page(self, slug):
        """Delete a test page"""
        # Make sure we're logged in
        self.login()

        return self.client.post(
            f'/content/page/{slug}/delete',
            follow_redirects=True
        )

    def create_tag(self, name='NewTag'):
        """Create a test tag"""
        # Make sure we're logged in
        self.login()

        return self.client.post(
            '/content/tag/new',
            data={
                'name': name
            },
            follow_redirects=True
        )

    def get_auth_token_header(self, email='test@example.com', password='password'):
        """Generate a Basic auth header for API token requests"""
        auth_string = base64.b64encode(f"{email}:{password}".encode()).decode()
        return {'Authorization': f'Basic {auth_string}'}
