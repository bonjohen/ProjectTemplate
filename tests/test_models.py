import unittest
from datetime import datetime, timezone
from app import create_app, db
from app.models import User, Role, Page, Tag, Media, PageVersion
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

    def test_user_full_name(self):
        """Test user full name functionality"""
        u = User(username='testuser', email='test@example.com')
        self.assertEqual(u.get_full_name(), 'testuser')

        u.first_name = 'John'
        u.last_name = 'Doe'
        self.assertEqual(u.get_full_name(), 'John Doe')

    def test_page_creation(self):
        """Test page creation"""
        user = User(username='author', email='author@example.com')
        db.session.add(user)
        db.session.commit()

        page = Page(
            title='Test Page',
            slug='test-page',
            content='This is a test page',
            summary='Test summary',
            is_published=True,
            user_id=user.id,
            created_at=datetime.now(timezone.utc),
            published_at=datetime.now(timezone.utc)
        )
        db.session.add(page)
        db.session.commit()

        retrieved_page = Page.query.filter_by(slug='test-page').first()
        self.assertIsNotNone(retrieved_page)
        self.assertEqual(retrieved_page.title, 'Test Page')
        self.assertEqual(retrieved_page.author.username, 'author')

    def test_tag_creation(self):
        """Test tag creation"""
        tag = Tag(name='TestTag')
        db.session.add(tag)
        db.session.commit()

        retrieved_tag = Tag.query.filter_by(name='TestTag').first()
        self.assertIsNotNone(retrieved_tag)
        self.assertEqual(retrieved_tag.name, 'TestTag')

    def test_page_tag_relationship(self):
        """Test relationship between pages and tags"""
        user = User(username='author2', email='author2@example.com')
        db.session.add(user)
        db.session.commit()

        tag1 = Tag(name='Tag1')
        tag2 = Tag(name='Tag2')
        db.session.add_all([tag1, tag2])
        db.session.commit()

        page = Page(
            title='Tagged Page',
            slug='tagged-page',
            content='This page has tags',
            user_id=user.id,
            created_at=datetime.now(timezone.utc)
        )
        page.tags.append(tag1)
        page.tags.append(tag2)
        db.session.add(page)
        db.session.commit()

        retrieved_page = Page.query.filter_by(slug='tagged-page').first()
        self.assertEqual(len(retrieved_page.tags), 2)
        self.assertIn(tag1, retrieved_page.tags)
        self.assertIn(tag2, retrieved_page.tags)

        # Test reverse relationship
        self.assertIn(page, tag1.pages)

if __name__ == '__main__':
    unittest.main()
