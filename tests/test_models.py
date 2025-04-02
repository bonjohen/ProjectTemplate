import unittest
from app import create_app, db
from app.models import User
from config import Config

class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # Use in-memory database for testing

class UserModelTestCase(unittest.TestCase):
    """Test case for User model"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_password_hashing(self):
        """Test password hashing works correctly"""
        u = User(username='test', email='test@example.com')
        u.set_password('password')
        self.assertTrue(u.check_password('password'))
        self.assertFalse(u.check_password('wrong_password'))
    
    def test_user_role(self):
        """Test user role functionality"""
        u = User(username='user', email='user@example.com', role='user')
        admin = User(username='admin', email='admin@example.com', role='admin')
        self.assertFalse(u.is_admin())
        self.assertTrue(admin.is_admin())

if __name__ == '__main__':
    unittest.main()
