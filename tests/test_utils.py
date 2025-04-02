"""
Test utilities for the application.
"""
import base64
import unittest
import socket
from unittest.mock import patch, MagicMock
from flask import session
from app.models import User, Tag, Page
from app.utils.port_utils import get_available_port
from datetime import datetime, timezone

def login(client, email, password):
    """Log in a user for testing"""
    return client.post(
        '/auth/login',
        data={
            'email': email,
            'password': password,
            'remember_me': False
        },
        follow_redirects=True
    )

def logout(client):
    """Log out a user for testing"""
    return client.get('/auth/logout', follow_redirects=True)

def create_user(username='testuser', email='test@example.com', password='password', role='user'):
    """Create a test user"""
    user = User(
        username=username,
        email=email,
        role=role,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_active=True
    )
    user.set_password(password)
    return user

def create_tag(name='TestTag'):
    """Create a test tag"""
    return Tag(name=name)

def create_page(title='Test Page', slug='test-page', content='Test content', user_id=1, is_published=True):
    """Create a test page"""
    page = Page(
        title=title,
        slug=slug,
        content=content,
        is_published=is_published,
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    if is_published:
        page.published_at = datetime.now(timezone.utc)
    return page

def get_auth_token_header(email, password):
    """Generate a Basic auth header for API token requests"""
    auth_string = base64.b64encode(f"{email}:{password}".encode()).decode()
    return {'Authorization': f'Basic {auth_string}'}

def set_logged_in_user(client, user_id):
    """Set a user as logged in for testing"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user_id)
        sess['_fresh'] = True


class PortUtilsTestCase(unittest.TestCase):
    """Test case for port utility functions"""

    @patch('socket.socket')
    def test_get_available_port_default_available(self, mock_socket):
        """Test get_available_port when default port is available"""
        # Mock socket to simulate default port being available
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Call the function
        port = get_available_port(5010)

        # Verify the result
        self.assertEqual(port, 5010)
        mock_socket_instance.bind.assert_called_once_with(('127.0.0.1', 5010))
        mock_socket_instance.close.assert_called_once()

    @patch('socket.socket')
    def test_get_available_port_default_unavailable(self, mock_socket):
        """Test get_available_port when default port is not available"""
        # Mock socket to simulate default port being unavailable
        mock_socket_instance1 = MagicMock()
        mock_socket_instance2 = MagicMock()

        # First socket raises OSError (port in use)
        mock_socket_instance1.bind.side_effect = OSError()

        # Second socket returns a dynamic port
        mock_socket_instance2.getsockname.return_value = ('127.0.0.1', 8888)

        # Configure mock to return different instances on each call
        mock_socket.side_effect = [mock_socket_instance1, mock_socket_instance2]

        # Call the function
        port = get_available_port(5010)

        # Verify the result
        self.assertEqual(port, 8888)
        mock_socket_instance1.bind.assert_called_once_with(('127.0.0.1', 5010))
        mock_socket_instance1.close.assert_called_once()
        mock_socket_instance2.bind.assert_called_once_with(('127.0.0.1', 0))
        mock_socket_instance2.close.assert_called_once()
