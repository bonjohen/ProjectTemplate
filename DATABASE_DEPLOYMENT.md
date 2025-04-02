# Database Deployment Guide

This document provides instructions for deploying and managing the application's persistent data components, including the SQLite database and ChromaDB.

## Deployment Styles

The application supports three deployment styles:

1. **Full Wipe**: All components of the application are removed.
2. **Full Install**: All components of the application are installed from scratch.
3. **Upgrade Install**: The persistent data components are updated in place.

## Using the Deployment Script

The `deploy_db.py` script provides a convenient way to manage the deployment process.

### Prerequisites

- Python 3.7 or higher
- Flask and its dependencies installed
- ChromaDB (optional, for vector database functionality)

### Basic Usage

```bash
# Auto-detect the appropriate deployment mode
python deploy_db.py --mode auto

# Full wipe (removes all data)
python deploy_db.py --mode wipe

# Full install (creates all components from scratch)
python deploy_db.py --mode install

# Upgrade install (updates existing components in place)
python deploy_db.py --mode upgrade
```

## Using Flask CLI Commands

The application also provides several Flask CLI commands for managing the database and ChromaDB.

### Database Management

```bash
# Initialize the database with required data
flask init-db

# Create an admin user
flask create-admin <username> <email> <password>

# Backup the database and ChromaDB
flask backup-db [backup_dir]

# Restore the database and ChromaDB from a backup
flask restore-db <backup_path>
```

### ChromaDB Management

```bash
# Initialize ChromaDB with required collections
flask init-chroma
```

## Database Migrations

The application uses Flask-Migrate (Alembic) for database migrations.

```bash
# Initialize migrations (first time only)
flask db init

# Create a migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Revert to a previous version
flask db downgrade
```

## Deployment Best Practices

1. **Always backup before making changes**:
   ```bash
   flask backup-db
   ```

2. **Use upgrade mode for production deployments**:
   ```bash
   python deploy_db.py --mode upgrade
   ```

3. **Test migrations on a staging environment first**:
   ```bash
   # On staging
   flask db upgrade
   # Verify everything works
   # Then on production
   flask db upgrade
   ```

4. **Monitor the logs during deployment**:
   ```bash
   tail -f deploy_db.log
   ```

## Troubleshooting

### Common Issues

1. **Database locked error**:
   - Ensure no other process is using the database
   - Restart the application

2. **Migration errors**:
   - Check the migration files in `migrations/versions/`
   - Consider using `flask db stamp head` to reset the migration state

3. **ChromaDB errors**:
   - Ensure ChromaDB is installed: `pip install chromadb`
   - Check the ChromaDB directory permissions

### Recovery

If something goes wrong, you can restore from a backup:

```bash
flask restore-db backups/20230101_120000
```

## Additional Information

- Database file location: `app.db`
- ChromaDB directory: `chroma_db/`
- Backup directory: `backups/`
- Migration files: `migrations/versions/`
