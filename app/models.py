from datetime import datetime, timezone
import jwt
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    """Load a user from the database"""
    return User.query.get(int(user_id))

# Association table for User and Role (many-to-many)
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    """User model for authentication and user management"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    bio = db.Column(db.Text)
    profile_image = db.Column(db.String(120), default='default.jpg')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    role = db.Column(db.String(20), default='user')  # 'admin', 'user', 'guest' - for backward compatibility

    # Relationships
    roles = db.relationship('Role', secondary=user_roles, lazy='subquery',
                         backref=db.backref('users', lazy=True))
    pages = db.relationship('Page', backref='author', lazy=True)
    media_files = db.relationship('Media', backref='owner', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Set the user's password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Check if the user has admin role"""
        return self.role == 'admin' or any(role.name == 'admin' for role in self.roles)

    def get_full_name(self):
        """Get the user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def to_dict(self):
        """Convert user object to dictionary for API responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'bio': self.bio,
            'profile_image': self.profile_image,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'role': self.role,
            'roles': [role.name for role in self.roles]
        }

    def get_reset_password_token(self, expires_in=3600):
        """Generate a token for password reset"""
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    def get_email_verification_token(self, expires_in=86400):
        """Generate a token for email verification (24 hours)"""
        return jwt.encode(
            {'verify_email': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_password_token(token):
        """Verify a password reset token"""
        try:
            id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )['reset_password']
        except:
            return None
        return User.query.get(id)

    @staticmethod
    def verify_email_token(token):
        """Verify an email verification token"""
        try:
            id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )['verify_email']
        except:
            return None
        return User.query.get(id)

class Role(db.Model):
    """Role model for role-based access control"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Role {self.name}>'

class Page(db.Model):
    """Page model for content management"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(200))
    featured_image = db.Column(db.String(120))
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    published_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    tags = db.relationship('Tag', secondary='page_tags', backref='pages')

    def __repr__(self):
        return f'<Page {self.title}>'

    def to_dict(self):
        """Convert page object to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'summary': self.summary,
            'featured_image': self.featured_image,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'author': self.author.username,
            'tags': [tag.name for tag in self.tags]
        }

# Association table for Page and Tag (many-to-many)
page_tags = db.Table('page_tags',
    db.Column('page_id', db.Integer, db.ForeignKey('page.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Tag(db.Model):
    """Tag model for content categorization"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Tag {self.name}>'

class Media(db.Model):
    """Media model for file uploads"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))  # e.g., 'image', 'document', 'video'
    file_size = db.Column(db.Integer)  # Size in bytes
    file_extension = db.Column(db.String(10))  # e.g., 'jpg', 'pdf', 'mp4'
    path = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(255))  # For accessibility
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Media {self.filename}>'

    def to_dict(self):
        """Convert media object to dictionary for API responses"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'file_extension': self.file_extension,
            'path': self.path,
            'alt_text': self.alt_text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'owner': self.owner.username
        }

class PageVersion(db.Model):
    """PageVersion model for tracking page revisions"""
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    page = db.relationship('Page', backref='versions')
    user = db.relationship('User', backref='page_versions')

    def __repr__(self):
        return f'<PageVersion {self.id} for Page {self.page_id}>'
