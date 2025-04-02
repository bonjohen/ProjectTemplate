import click
import os
import shutil
from flask.cli import with_appcontext
from datetime import datetime, timezone
from app import db
from app.models import User, Role, Tag

# Try to import ChromaDB utilities
try:
    from app.utils.chroma_utils import initialize_chroma, upgrade_chroma
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

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

@click.command('init-chroma')
@with_appcontext
def init_chroma_command():
    """Initialize ChromaDB with required collections."""
    if not CHROMA_AVAILABLE:
        click.echo('ChromaDB utilities are not available. Make sure chromadb is installed.')
        return

    if initialize_chroma():
        click.echo('ChromaDB initialized successfully.')
    else:
        click.echo('Failed to initialize ChromaDB.')

@click.command('backup-db')
@click.argument('backup_dir', default='backups')
@with_appcontext
def backup_db_command(backup_dir):
    """Backup the database and ChromaDB."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, timestamp)

    # Create backup directory if it doesn't exist
    os.makedirs(backup_path, exist_ok=True)

    # Backup SQLite database if it exists
    db_file = 'app.db'
    if os.path.exists(db_file):
        db_backup_path = os.path.join(backup_path, db_file)
        shutil.copy2(db_file, db_backup_path)
        click.echo(f'Database backed up to {db_backup_path}')

    # Backup ChromaDB if it exists
    chroma_dir = 'chroma_db'
    if os.path.exists(chroma_dir):
        chroma_backup_path = os.path.join(backup_path, "chroma_db")
        shutil.copytree(chroma_dir, chroma_backup_path)
        click.echo(f'ChromaDB backed up to {chroma_backup_path}')

    click.echo(f'Backup completed successfully to {backup_path}')

@click.command('restore-db')
@click.argument('backup_path')
@with_appcontext
def restore_db_command(backup_path):
    """Restore the database and ChromaDB from a backup."""
    if not os.path.exists(backup_path):
        click.echo(f'Backup path {backup_path} does not exist.')
        return

    # Restore SQLite database if it exists in the backup
    db_file = 'app.db'
    backup_db_path = os.path.join(backup_path, db_file)
    if os.path.exists(backup_db_path):
        # Stop the Flask application if it's running
        click.echo('Restoring database...')
        shutil.copy2(backup_db_path, db_file)
        click.echo(f'Database restored from {backup_db_path}')

    # Restore ChromaDB if it exists in the backup
    chroma_dir = 'chroma_db'
    backup_chroma_path = os.path.join(backup_path, chroma_dir)
    if os.path.exists(backup_chroma_path):
        click.echo('Restoring ChromaDB...')
        if os.path.exists(chroma_dir):
            shutil.rmtree(chroma_dir)
        shutil.copytree(backup_chroma_path, chroma_dir)
        click.echo(f'ChromaDB restored from {backup_chroma_path}')

    click.echo('Restore completed successfully')

def register_commands(app):
    """Register CLI commands with the Flask application."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(init_chroma_command)
    app.cli.add_command(backup_db_command)
    app.cli.add_command(restore_db_command)
