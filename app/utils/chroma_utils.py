"""
Utility functions for ChromaDB management.
"""
import os
import logging
from pathlib import Path

# Try to import chromadb, but don't fail if it's not installed
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

logger = logging.getLogger(__name__)

# Constants
CHROMA_DIR = "chroma_db"

def get_chroma_client():
    """
    Get a ChromaDB client.
    
    Returns:
        A ChromaDB client if ChromaDB is available, None otherwise.
    """
    if not CHROMA_AVAILABLE:
        logger.warning("ChromaDB is not installed. Install it with 'pip install chromadb'.")
        return None
    
    # Create the ChromaDB directory if it doesn't exist
    os.makedirs(CHROMA_DIR, exist_ok=True)
    
    # Create a persistent client
    client = chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(
            anonymized_telemetry=False
        )
    )
    
    return client

def initialize_chroma():
    """
    Initialize ChromaDB with default collections.
    
    Returns:
        True if initialization was successful, False otherwise.
    """
    if not CHROMA_AVAILABLE:
        logger.warning("ChromaDB is not installed. Install it with 'pip install chromadb'.")
        return False
    
    try:
        client = get_chroma_client()
        if client is None:
            return False
        
        # Create default collections if they don't exist
        # Example: Create a collection for pages
        try:
            pages_collection = client.get_or_create_collection(
                name="pages",
                metadata={"description": "Collection for page content"}
            )
            logger.info("Created or retrieved 'pages' collection")
        except Exception as e:
            logger.error(f"Error creating 'pages' collection: {e}")
            return False
        
        # Example: Create a collection for user data
        try:
            users_collection = client.get_or_create_collection(
                name="users",
                metadata={"description": "Collection for user data"}
            )
            logger.info("Created or retrieved 'users' collection")
        except Exception as e:
            logger.error(f"Error creating 'users' collection: {e}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error initializing ChromaDB: {e}")
        return False

def upgrade_chroma():
    """
    Upgrade ChromaDB collections.
    
    This function should handle any necessary changes to ChromaDB collections
    when upgrading the application.
    
    Returns:
        True if upgrade was successful, False otherwise.
    """
    if not CHROMA_AVAILABLE:
        logger.warning("ChromaDB is not installed. Install it with 'pip install chromadb'.")
        return False
    
    try:
        client = get_chroma_client()
        if client is None:
            return False
        
        # Get existing collections
        collections = client.list_collections()
        collection_names = [c.name for c in collections]
        
        # Add any new collections that should exist
        if "pages" not in collection_names:
            try:
                pages_collection = client.create_collection(
                    name="pages",
                    metadata={"description": "Collection for page content"}
                )
                logger.info("Created 'pages' collection during upgrade")
            except Exception as e:
                logger.error(f"Error creating 'pages' collection during upgrade: {e}")
                return False
        
        if "users" not in collection_names:
            try:
                users_collection = client.create_collection(
                    name="users",
                    metadata={"description": "Collection for user data"}
                )
                logger.info("Created 'users' collection during upgrade")
            except Exception as e:
                logger.error(f"Error creating 'users' collection during upgrade: {e}")
                return False
        
        # Perform any necessary migrations on existing collections
        # Example: Update metadata on an existing collection
        if "pages" in collection_names:
            pages_collection = client.get_collection("pages")
            # Update metadata if needed
            # pages_collection.modify(metadata={"description": "Updated description"})
        
        return True
    except Exception as e:
        logger.error(f"Error upgrading ChromaDB: {e}")
        return False
