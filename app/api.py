from flask import Blueprint, jsonify, request, current_app, url_for
from flask_login import current_user
from werkzeug.security import generate_password_hash
from functools import wraps
from datetime import datetime, timezone
import jwt
from app import db, cache
from app.models import User, Page, Tag, Media

# Create blueprint
api = Blueprint('api', __name__)

def token_required(f):
    """Decorator for requiring API token authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])

            if not current_user:
                return jsonify({'message': 'User not found!'}), 401

        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@api.route('/token', methods=['POST'])
def get_token():
    """Generate API token with username/password authentication"""
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic realm="Login required!"'}), 401

    user = User.query.filter_by(email=auth.username).first()

    if not user:
        return jsonify({'message': 'User not found!'}), 401

    if user.check_password(auth.password):
        # Generate token
        token = jwt.encode(
            {
                'user_id': user.id,
                'exp': datetime.now(timezone.utc).timestamp() + 3600  # 1 hour expiration
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials!'}), 401

# User endpoints
@api.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    """Get all users (admin only)"""
    if not current_user.is_admin():
        return jsonify({'message': 'Permission denied!'}), 403

    users = User.query.all()
    return jsonify({'users': [user.to_dict() for user in users]})

@api.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    """Get a specific user"""
    # Users can only access their own data unless they're admin
    if current_user.id != user_id and not current_user.is_admin():
        return jsonify({'message': 'Permission denied!'}), 403

    user = User.query.get_or_404(user_id)
    return jsonify({'user': user.to_dict()})

@api.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()

    if not data or not data.get('email') or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing required fields!'}), 400

    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered!'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already taken!'}), 400

    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        created_at=datetime.now(timezone.utc),
        role='user'
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully!', 'user': user.to_dict()}), 201

@api.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    """Update a user"""
    # Users can only update their own data unless they're admin
    if current_user.id != user_id and not current_user.is_admin():
        return jsonify({'message': 'Permission denied!'}), 403

    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No input data provided!'}), 400

    # Update fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'bio' in data:
        user.bio = data['bio']

    # Only admin can update role
    if 'role' in data and current_user.is_admin():
        user.role = data['role']

    # Handle password update
    if 'password' in data:
        user.set_password(data['password'])

    user.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({'message': 'User updated successfully!', 'user': user.to_dict()})

@api.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    """Delete a user (admin only or self)"""
    if current_user.id != user_id and not current_user.is_admin():
        return jsonify({'message': 'Permission denied!'}), 403

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully!'})

# Page endpoints
@api.route('/pages', methods=['GET'])
@cache.cached(timeout=60)  # Cache for 1 minute
def get_pages():
    """Get all published pages"""
    pages = Page.query.filter_by(is_published=True).all()
    return jsonify({'pages': [page.to_dict() for page in pages]})

@api.route('/pages/<int:page_id>', methods=['GET'])
@cache.cached(timeout=60, query_string=True)  # Cache for 1 minute
def get_page(page_id):
    """Get a specific page"""
    page = Page.query.get_or_404(page_id)

    # If page is not published, only allow author or admin to view
    if not page.is_published:
        if not current_user.is_authenticated or (current_user.id != page.user_id and not current_user.is_admin()):
            return jsonify({'message': 'Page not found!'}), 404

    return jsonify({'page': page.to_dict()})

@api.route('/pages', methods=['POST'])
@token_required
def create_page(current_user):
    """Create a new page"""
    data = request.get_json()

    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'message': 'Missing required fields!'}), 400

    # Create new page
    page = Page(
        title=data['title'],
        slug=data.get('slug', data['title'].lower().replace(' ', '-')),
        content=data['content'],
        summary=data.get('summary', ''),
        is_published=data.get('is_published', False),
        user_id=current_user.id,
        created_at=datetime.now(timezone.utc)
    )

    # Set published date if publishing
    if page.is_published:
        page.published_at = datetime.now(timezone.utc)

    # Add tags if provided
    if 'tags' in data and isinstance(data['tags'], list):
        for tag_name in data['tags']:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            page.tags.append(tag)

    db.session.add(page)
    db.session.commit()

    return jsonify({'message': 'Page created successfully!', 'page': page.to_dict()}), 201

@api.route('/pages/<int:page_id>', methods=['PUT'])
@token_required
def update_page(current_user, page_id):
    """Update a page"""
    page = Page.query.get_or_404(page_id)

    # Check if user is authorized to edit (author or admin)
    if page.user_id != current_user.id and not current_user.is_admin():
        return jsonify({'message': 'Permission denied!'}), 403

    data = request.get_json()

    if not data:
        return jsonify({'message': 'No input data provided!'}), 400

    # Update fields
    if 'title' in data:
        page.title = data['title']
    if 'slug' in data:
        page.slug = data['slug']
    if 'content' in data:
        page.content = data['content']
    if 'summary' in data:
        page.summary = data['summary']

    # Handle published status change
    if 'is_published' in data:
        if not page.is_published and data['is_published']:
            page.published_at = datetime.now(timezone.utc)
        page.is_published = data['is_published']

    # Update tags if provided
    if 'tags' in data and isinstance(data['tags'], list):
        # Clear existing tags
        page.tags = []

        # Add new tags
        for tag_name in data['tags']:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            page.tags.append(tag)

    page.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({'message': 'Page updated successfully!', 'page': page.to_dict()})

@api.route('/pages/<int:page_id>', methods=['DELETE'])
@token_required
def delete_page(current_user, page_id):
    """Delete a page"""
    page = Page.query.get_or_404(page_id)

    # Check if user is authorized to delete (author or admin)
    if page.user_id != current_user.id and not current_user.is_admin():
        return jsonify({'message': 'Permission denied!'}), 403

    db.session.delete(page)
    db.session.commit()

    return jsonify({'message': 'Page deleted successfully!'})

# Tag endpoints
@api.route('/tags', methods=['GET'])
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_tags():
    """Get all tags"""
    tags = Tag.query.all()
    return jsonify({'tags': [{'id': tag.id, 'name': tag.name} for tag in tags]})

@api.route('/tags/<int:tag_id>', methods=['GET'])
def get_tag(tag_id):
    """Get a specific tag and its pages"""
    tag = Tag.query.get_or_404(tag_id)

    # Get published pages with this tag
    pages = [page.to_dict() for page in tag.pages if page.is_published]

    return jsonify({
        'tag': {'id': tag.id, 'name': tag.name},
        'pages': pages
    })

@api.route('/tags', methods=['POST'])
@token_required
def create_tag(current_user):
    """Create a new tag"""
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'message': 'Missing required fields!'}), 400

    # Check if tag already exists
    if Tag.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'Tag already exists!'}), 400

    # Create new tag
    tag = Tag(name=data['name'])
    db.session.add(tag)
    db.session.commit()

    return jsonify({'message': 'Tag created successfully!', 'tag': {'id': tag.id, 'name': tag.name}}), 201

@api.route('/tags/<int:tag_id>', methods=['PUT'])
@token_required
def update_tag(current_user, tag_id):
    """Update a tag (admin only)"""
    if not current_user.is_admin():
        return jsonify({'message': 'Permission denied!'}), 403

    tag = Tag.query.get_or_404(tag_id)
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'message': 'Missing required fields!'}), 400

    # Check if new name already exists
    existing_tag = Tag.query.filter_by(name=data['name']).first()
    if existing_tag and existing_tag.id != tag_id:
        return jsonify({'message': 'Tag name already exists!'}), 400

    tag.name = data['name']
    db.session.commit()

    return jsonify({'message': 'Tag updated successfully!', 'tag': {'id': tag.id, 'name': tag.name}})

@api.route('/tags/<int:tag_id>', methods=['DELETE'])
@token_required
def delete_tag(current_user, tag_id):
    """Delete a tag (admin only)"""
    if not current_user.is_admin():
        return jsonify({'message': 'Permission denied!'}), 403

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()

    return jsonify({'message': 'Tag deleted successfully!'})
