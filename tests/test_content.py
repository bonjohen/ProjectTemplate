import unittest
from app.models import User, Page, Tag
from tests.base import BaseTestCase

class ContentTestCase(BaseTestCase):
    """Test case for content management functionality"""

    def setUp(self):
        """Set up test environment"""
        super().setUp()
        # Login the user
        self.login()

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
        response = self.create_page()
        self.assertEqual(response.status_code, 200)

        # Verify page was created in database
        page = Page.query.filter_by(slug='test-page').first()
        self.assertIsNotNone(page)
        self.assertEqual(page.title, 'Test Page')
        self.assertEqual(page.user_id, self.user.id)
        # Check if the page appears in the pages list
        response = self.client.get('/content/pages')
        self.assertIn(b'Test Page', response.data)

    def test_edit_page(self):
        """Test editing a page"""
        # First create a page directly in the database
        page = Page(
            title='Original Title',
            slug='original-slug',
            content='Original content',
            user_id=self.user.id,
            is_published=True
        )
        self.db.session.add(page)
        self.db.session.commit()

        # Then edit it
        response = self.edit_page('original-slug')
        self.assertEqual(response.status_code, 200)

        # Verify page was updated in database
        updated_page = Page.query.filter_by(slug='updated-slug').first()
        self.assertIsNotNone(updated_page)
        self.assertEqual(updated_page.title, 'Updated Title')
        # Check if the updated page appears in the pages list
        response = self.client.get('/content/pages')
        self.assertIn(b'Updated Title', response.data)

    def test_delete_page(self):
        """Test deleting a page"""
        # First create a page directly in the database
        page = Page(
            title='Page to Delete',
            slug='page-to-delete',
            content='This page will be deleted',
            user_id=self.user.id,
            is_published=True
        )
        self.db.session.add(page)
        self.db.session.commit()

        # Then delete it
        response = self.delete_page('page-to-delete')
        self.assertEqual(response.status_code, 200)

        # Verify page was deleted from database
        deleted_page = Page.query.filter_by(slug='page-to-delete').first()
        self.assertIsNone(deleted_page)

    def test_tags_route(self):
        """Test tags list route"""
        response = self.client.get('/content/tags')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tags', response.data)
        self.assertIn(b'TestTag', response.data)

    def test_create_tag(self):
        """Test creating a new tag"""
        response = self.create_tag('NewTag')
        self.assertEqual(response.status_code, 200)

        # Verify tag was created in database
        tag = Tag.query.filter_by(name='NewTag').first()
        self.assertIsNotNone(tag)
        self.assertEqual(tag.name, 'NewTag')

        # Check if the tag appears in the tags list
        response = self.client.get('/content/tags')
        self.assertIn(b'NewTag', response.data)

if __name__ == '__main__':
    unittest.main()
