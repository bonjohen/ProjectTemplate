import unittest
from app.models import User
from tests.base import BaseTestCase

class AuthTestCase(BaseTestCase):
    """Test case for authentication functionality"""

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
        result = self.login()
        self.assertTrue(result)
        # Check if we can access a protected page
        response = self.client.get('/content/page/new')
        self.assertEqual(response.status_code, 200)

    def test_login_failure(self):
        """Test failed login"""
        result = self.login(password='wrongpassword')
        self.assertFalse(result)
        # Check if we're redirected when trying to access a protected page
        response = self.client.get('/content/page/new')
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        """Test logout functionality"""
        # First login
        self.login()

        # Then logout
        self.logout()

        # Check if we're redirected when trying to access a protected page
        response = self.client.get('/content/page/new')
        self.assertEqual(response.status_code, 302)

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

        # Verify user was created in database
        user = User.query.filter_by(email='new@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'newuser')

    def test_protected_route(self):
        """Test that protected routes require login"""
        # Try to access protected page without login
        response = self.client.get('/content/page/new')
        self.assertEqual(response.status_code, 302)  # Should redirect to login

        # Login
        self.login()

        # Try to access protected page after login
        response = self.client.get('/content/page/new')
        self.assertEqual(response.status_code, 200)  # Should be accessible

if __name__ == '__main__':
    unittest.main()
