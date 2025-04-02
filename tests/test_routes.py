import unittest
from app import create_app, db
from app.models import User
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

if __name__ == '__main__':
    unittest.main()
