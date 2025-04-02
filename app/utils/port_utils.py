"""
Utility functions for port management.
"""
import socket
import logging

logger = logging.getLogger(__name__)

def get_available_port(default_port=5010):
    """
    Get an available port, starting with the default port.
    If the default port is not available, find another available port.
    
    Args:
        default_port: The preferred port to use
        
    Returns:
        An available port number
    """
    port = default_port
    
    # Try the default port first
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('127.0.0.1', port))
        s.close()
        logger.info(f"Using default port: {port}")
        return port
    except OSError:
        logger.warning(f"Default port {port} is not available")
        s.close()
    
    # If default port is not available, find another port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))  # Let OS assign a free port
    port = s.getsockname()[1]
    s.close()
    logger.info(f"Using dynamically assigned port: {port}")
    return port
