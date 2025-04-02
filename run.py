import os
from app import create_app, db
from app.models import User, Role, Page, Tag, Media, PageVersion
from app.utils.port_utils import get_available_port

# Get configuration from environment variable or use default
config_name = os.environ.get('FLASK_CONFIG', 'development')
app = create_app(config_name)

@app.shell_context_processor
def make_shell_context():
    """Add database and models to flask shell context"""
    return {
        'db': db,
        'User': User,
        'Role': Role,
        'Page': Page,
        'Tag': Tag,
        'Media': Media,
        'PageVersion': PageVersion
    }

if __name__ == '__main__':
    # Get port based on configuration
    default_port = app.config.get('DEFAULT_PORT', 5010)

    if app.config.get('USE_DYNAMIC_PORT', False):
        port = get_available_port(default_port)
    else:
        port = default_port

    app.run(port=port)
