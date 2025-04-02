import unittest
from flask import url_for
from app import create_app, db
from app.models import User
from config import Config

class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # Use in-memory database for testing
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost:5010'  # Needed for url_for to work in tests

class AuthTestCase(unittest.TestCase):
    """Test case for authentication functionality"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
    
    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_login_page(self):
        """Test login page loads correctly"""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data)
    
    def test_register_page(self):
        """Test register page loads correctly"""
        response = self.client.get('/auth/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create an Account', response.data)
    
    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(
            '/auth/login',
            data={
                'email': 'test@example.com',
                'password': 'password',
                'remember_me': False
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged in successfully', response.data)
    
    def test_login_failure(self):
        """Test failed login"""
        response = self.client.post(
            '/auth/login',
            data={
                'email': 'test@example.com',
                'password': 'wrongpassword',
                'remember_me': False
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email or password', response.data)
    
    def test_logout(self):
        """Test logout functionality"""
        # First login
        self.client.post(
            '/auth/login',
            data={
                'email': 'test@example.com',
                'password': 'password',
                'remember_me': False
            }
        )
        
        # Then logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out successfully', response.data)
    
    def test_register_user(self):
        """Test user registration"""
        response = self.client.post(
            '/auth/register',
            data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'newpassword',
                'confirm_password': 'newpassword'
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your account has been created', response.data)
        
        # Verify user was created in database
        user = User.query.filter_by(email='new@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'newuser')
    
    def test_protected_route(self):
        """Test that protected routes require login"""
        # Try to access dashboard without login
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please log in to access this page', response.data)
        
        # Login
        self.client.post(
            '/auth/login',
            data={
                'email': 'test@example.com',
                'password': 'password',
                'remember_me': False
            }
        )
        
        # Try to access dashboard after login
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)

if __name__ == '__main__':
    unittest.main()
