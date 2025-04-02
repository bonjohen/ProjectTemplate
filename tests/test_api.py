import unittest
import json
import base64
from app.models import User, Page, Tag
from datetime import datetime, timezone
from tests.base import BaseTestCase
from app import db

class APITestCase(BaseTestCase):
    """Test case for API endpoints"""

    def setUp(self):
        """Set up test environment before each test"""
        super().setUp()

        # Create admin user
        self.admin = User(
            username='admin',
            email='admin@example.com',
            role='admin',
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        self.admin.set_password('adminpassword')
        db.session.add(self.admin)

        # Create test page
        self.page = Page(
            title='Test Page',
            slug='test-page',
            content='This is a test page',
            is_published=True,
            user_id=1,  # Will be assigned to testuser
            created_at=datetime.now(timezone.utc),
            published_at=datetime.now(timezone.utc)
        )
        db.session.add(self.page)

        # Add tag to page
        self.page.tags.append(self.tag)

        db.session.commit()

    def get_token(self, email='test@example.com', password='password'):
        """Helper method to get authentication token"""
        auth_string = base64.b64encode(f"{email}:{password}".encode()).decode()
        response = self.client.post(
            '/api/token',
            headers={'Authorization': f'Basic {auth_string}'}
        )
        return json.loads(response.data)['token']

    def test_get_token(self):
        """Test token generation"""
        auth_string = base64.b64encode("test@example.com:password".encode()).decode()
        response = self.client.post(
            '/api/token',
            headers={'Authorization': f'Basic {auth_string}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)

    def test_get_pages(self):
        """Test getting all pages"""
        response = self.client.get('/api/pages')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('pages', data)
        self.assertEqual(len(data['pages']), 1)
        self.assertEqual(data['pages'][0]['title'], 'Test Page')

    def test_get_page(self):
        """Test getting a specific page"""
        response = self.client.get(f'/api/pages/{self.page.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('page', data)
        self.assertEqual(data['page']['title'], 'Test Page')

    def test_get_tags(self):
        """Test getting all tags"""
        response = self.client.get('/api/tags')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('tags', data)
        self.assertEqual(len(data['tags']), 1)
        self.assertEqual(data['tags'][0]['name'], 'TestTag')

    def test_create_user(self):
        """Test creating a new user"""
        response = self.client.post(
            '/api/users',
            json={
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'newpassword'
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], 'newuser')

        # Verify user was created in database
        user = User.query.filter_by(email='new@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'newuser')

if __name__ == '__main__':
    unittest.main()
