"""
Database deployment script for the application.

This script provides three deployment styles:
1. Full Wipe: All components of the application are removed.
2. Full Install: All components of the application are installed.
3. Upgrade Install: The persistent data components are updated in place.
"""
import os
import sys
import shutil
import argparse
import subprocess
from datetime import datetime
import sqlite3
import logging
from pathlib import Path
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("deploy_db.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
BACKUP_DIR = "backups"
DB_FILE = "app.db"
MIGRATIONS_DIR = "migrations"
CHROMA_DIR = "chroma_db"

def create_backup():
    """Create a backup of the database and other persistent data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, timestamp)

    # Create backup directory if it doesn't exist
    os.makedirs(backup_path, exist_ok=True)

    # Backup SQLite database if it exists
    if os.path.exists(DB_FILE):
        db_backup_path = os.path.join(backup_path, DB_FILE)
        shutil.copy2(DB_FILE, db_backup_path)
        logger.info(f"Database backed up to {db_backup_path}")

    # Backup ChromaDB if it exists
    if os.path.exists(CHROMA_DIR):
        chroma_backup_path = os.path.join(backup_path, "chroma_db")
        shutil.copytree(CHROMA_DIR, chroma_backup_path)
        logger.info(f"ChromaDB backed up to {chroma_backup_path}")

    # Backup migrations
    if os.path.exists(MIGRATIONS_DIR):
        migrations_backup_path = os.path.join(backup_path, "migrations")
        shutil.copytree(MIGRATIONS_DIR, migrations_backup_path)
        logger.info(f"Migrations backed up to {migrations_backup_path}")

    return backup_path

def run_command(command, error_message=None):
    """Run a shell command and handle errors"""
    try:
        logger.info(f"Running command: {command}")
        result = subprocess.run(command, shell=True, check=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
        logger.info(f"Command output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        if error_message:
            logger.error(f"{error_message}: {e}")
        logger.error(f"Command failed with error: {e.stderr}")
        return False

def full_wipe():
    """Remove all components of the application"""
    logger.info("Starting full wipe...")

    # Create backup before wiping
    backup_path = create_backup()
    logger.info(f"Backup created at {backup_path}")

    # Remove database file
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        logger.info(f"Removed database file: {DB_FILE}")

    # Remove ChromaDB directory
    if os.path.exists(CHROMA_DIR):
        shutil.rmtree(CHROMA_DIR)
        logger.info(f"Removed ChromaDB directory: {CHROMA_DIR}")

    # Remove migrations directory
    if os.path.exists(MIGRATIONS_DIR):
        shutil.rmtree(MIGRATIONS_DIR)
        logger.info(f"Removed migrations directory: {MIGRATIONS_DIR}")

    logger.info("Full wipe completed successfully")
    return True

def full_install():
    """Install all components of the application"""
    logger.info("Starting full installation...")

    # Initialize migrations
    if not os.path.exists(MIGRATIONS_DIR):
        if not run_command("flask db init", "Failed to initialize migrations"):
            return False
        logger.info("Migrations initialized")

    # Create migration
    if not run_command("flask db migrate", "Failed to create migration"):
        return False
    logger.info("Migration created")

    # Apply migration
    if not run_command("flask db upgrade", "Failed to apply migration"):
        return False
    logger.info("Migration applied")

    # Initialize database with seed data
    if not run_command("flask init-db", "Failed to initialize database with seed data"):
        return False
    logger.info("Database initialized with seed data")

    # Initialize ChromaDB
    try:
        # Import the ChromaDB utility module
        from app.utils.chroma_utils import initialize_chroma

        if initialize_chroma():
            logger.info("ChromaDB initialized successfully")
        else:
            logger.warning("Failed to initialize ChromaDB")
    except ImportError:
        logger.warning("ChromaDB utilities not available")

    logger.info("Full installation completed successfully")
    return True

def upgrade_install():
    """Update the persistent data components in place"""
    logger.info("Starting upgrade installation...")

    # Create backup before upgrading
    backup_path = create_backup()
    logger.info(f"Backup created at {backup_path}")

    # Create migration for schema changes
    if not run_command("flask db migrate", "Failed to create migration"):
        return False
    logger.info("Migration created")

    # Apply migration (this will perform ALTER TABLE instead of DROP/CREATE)
    if not run_command("flask db upgrade", "Failed to apply migration"):
        return False
    logger.info("Migration applied")

    # Update ChromaDB
    try:
        # Import the ChromaDB utility module
        from app.utils.chroma_utils import upgrade_chroma

        if upgrade_chroma():
            logger.info("ChromaDB upgraded successfully")
        else:
            logger.warning("Failed to upgrade ChromaDB")
    except ImportError:
        logger.warning("ChromaDB utilities not available")

    logger.info("Upgrade installation completed successfully")
    return True

def check_database_exists():
    """Check if the database file exists and has tables"""
    if not os.path.exists(DB_FILE):
        return False

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()

        # Check if there are any tables
        return len(tables) > 0
    except sqlite3.Error as e:
        logger.error(f"Error checking database: {e}")
        return False

def main():
    """Main function to handle deployment"""
    parser = argparse.ArgumentParser(description="Database deployment script")
    parser.add_argument("--mode", choices=["wipe", "install", "upgrade", "auto"],
                      default="auto", help="Deployment mode")
    args = parser.parse_args()

    # Create backup directory if it doesn't exist
    os.makedirs(BACKUP_DIR, exist_ok=True)

    mode = args.mode

    # Auto-detect mode if not specified
    if mode == "auto":
        if check_database_exists():
            mode = "upgrade"
        else:
            mode = "install"
        logger.info(f"Auto-detected mode: {mode}")

    # Execute the selected mode
    if mode == "wipe":
        if full_wipe():
            logger.info("Full wipe completed successfully")
        else:
            logger.error("Full wipe failed")
            return 1
    elif mode == "install":
        if full_install():
            logger.info("Full installation completed successfully")
        else:
            logger.error("Full installation failed")
            return 1
    elif mode == "upgrade":
        if upgrade_install():
            logger.info("Upgrade installation completed successfully")
        else:
            logger.error("Upgrade installation failed")
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
