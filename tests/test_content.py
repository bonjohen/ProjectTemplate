import unittest
import io
from flask import url_for
from app import create_app, db
from app.models import User, Page, Tag
from config import Config

class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # Use in-memory database for testing
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost:5010'  # Needed for url_for to work in tests

class ContentTestCase(unittest.TestCase):
    """Test case for content management functionality"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password')
        db.session.add(self.user)
        
        # Create test tag
        self.tag = Tag(name='TestTag')
        db.session.add(self.tag)
        
        db.session.commit()
        
        # Login the user
        self.client.post(
            '/auth/login',
            data={
                'email': 'test@example.com',
                'password': 'password',
                'remember_me': False
            }
        )
    
    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_pages_route(self):
        """Test pages list route"""
        response = self.client.get('/content/pages')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Pages', response.data)
    
    def test_create_page_route(self):
        """Test page creation route"""
        response = self.client.get('/content/page/new')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New Page', response.data)
    
    def test_create_page(self):
        """Test creating a new page"""
        response = self.client.post(
            '/content/page/new',
            data={
                'title': 'Test Page',
                'slug': 'test-page',
                'content': 'This is a test page',
                'summary': 'Test summary',
                'is_published': True,
                'tags': [self.tag.id]
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your page has been created', response.data)
        
        # Verify page was created in database
        page = Page.query.filter_by(slug='test-page').first()
        self.assertIsNotNone(page)
        self.assertEqual(page.title, 'Test Page')
        self.assertEqual(page.author.username, 'testuser')
        self.assertEqual(len(page.tags), 1)
        self.assertEqual(page.tags[0].name, 'TestTag')
    
    def test_edit_page(self):
        """Test editing a page"""
        # First create a page
        page = Page(
            title='Original Title',
            slug='original-slug',
            content='Original content',
            user_id=self.user.id
        )
        db.session.add(page)
        db.session.commit()
        
        # Then edit it
        response = self.client.post(
            f'/content/page/original-slug/edit',
            data={
                'title': 'Updated Title',
                'slug': 'updated-slug',
                'content': 'Updated content',
                'summary': 'Updated summary',
                'is_published': True,
                'tags': [self.tag.id]
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your page has been updated', response.data)
        
        # Verify page was updated in database
        page = Page.query.filter_by(slug='updated-slug').first()
        self.assertIsNotNone(page)
        self.assertEqual(page.title, 'Updated Title')
        self.assertEqual(page.content, 'Updated content')
    
    def test_delete_page(self):
        """Test deleting a page"""
        # First create a page
        page = Page(
            title='Page to Delete',
            slug='page-to-delete',
            content='This page will be deleted',
            user_id=self.user.id
        )
        db.session.add(page)
        db.session.commit()
        
        # Then delete it
        response = self.client.post(
            f'/content/page/page-to-delete/delete',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your page has been deleted', response.data)
        
        # Verify page was deleted from database
        page = Page.query.filter_by(slug='page-to-delete').first()
        self.assertIsNone(page)
    
    def test_tags_route(self):
        """Test tags list route"""
        response = self.client.get('/content/tags')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tags', response.data)
        self.assertIn(b'TestTag', response.data)
    
    def test_create_tag(self):
        """Test creating a new tag"""
        response = self.client.post(
            '/content/tag/new',
            data={
                'name': 'NewTag'
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your tag has been created', response.data)
        
        # Verify tag was created in database
        tag = Tag.query.filter_by(name='NewTag').first()
        self.assertIsNotNone(tag)
        self.assertEqual(tag.name, 'NewTag')

if __name__ == '__main__':
    unittest.main()
