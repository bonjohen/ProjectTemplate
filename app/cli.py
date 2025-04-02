import click
from flask.cli import with_appcontext
from datetime import datetime, timezone
from app import db
from app.models import User, Role, Tag

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database with required data."""
    # Create default roles
    admin_role = Role(name='admin', description='Administrator')
    user_role = Role(name='user', description='Regular user')
    guest_role = Role(name='guest', description='Guest user')
    
    db.session.add_all([admin_role, user_role, guest_role])
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@example.com',
        is_active=True,
        email_verified=True,
        role='admin',
        created_at=datetime.now(timezone.utc)
    )
    admin.set_password('adminpassword')  # Change in production!
    
    db.session.add(admin)
    
    # Create default tags
    default_tags = [
        Tag(name='General'),
        Tag(name='Tutorial'),
        Tag(name='News'),
        Tag(name='Documentation')
    ]
    db.session.add_all(default_tags)
    
    db.session.commit()
    click.echo('Database initialized with default data.')

@click.command('create-admin')
@click.argument('username')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_admin_command(username, email, password):
    """Create a new admin user."""
    user = User.query.filter_by(email=email).first()
    
    if user:
        click.echo(f'User with email {email} already exists.')
        return
    
    user = User(
        username=username,
        email=email,
        is_active=True,
        email_verified=True,
        role='admin',
        created_at=datetime.now(timezone.utc)
    )
    user.set_password(password)
    
    # Add admin role
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin', description='Administrator')
        db.session.add(admin_role)
    
    user.roles.append(admin_role)
    db.session.add(user)
    db.session.commit()
    
    click.echo(f'Admin user {username} created successfully.')

def register_commands(app):
    """Register CLI commands with the Flask application."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
