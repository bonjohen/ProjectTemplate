import unittest
from flask import url_for
from app import create_app, db
from app.models import User, Page, Tag, Role
from config import Config

class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # Use in-memory database for testing
    WTF_CSRF_ENABLED = False

class RoutesTestCase(unittest.TestCase):
    """Test case for application routes"""

    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index_page(self):
        """Test the index page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to Python Web App', response.data)

    def test_dashboard_redirect(self):
        """Test that dashboard redirects when not logged in"""
        response = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Should redirect

    def test_pages_route(self):
        """Test the pages route loads correctly"""
        response = self.client.get('/content/pages')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Pages', response.data)

    def test_api_docs_route(self):
        """Test the API documentation page loads correctly"""
        response = self.client.get('/api-docs')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'API Documentation', response.data)

    def test_sitemap_route(self):
        """Test the sitemap page loads correctly"""
        response = self.client.get('/sitemap')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sitemap', response.data)

    def test_api_pages_endpoint(self):
        """Test the API pages endpoint returns JSON"""
        response = self.client.get('/api/pages')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

    def test_api_tags_endpoint(self):
        """Test the API tags endpoint returns JSON"""
        response = self.client.get('/api/tags')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

if __name__ == '__main__':
    unittest.main()
