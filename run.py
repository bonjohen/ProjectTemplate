import os
from app import create_app, db
from app.models import User, Role, Page, Tag, Media, PageVersion

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
    # Use port from environment variable or default to 5010
    port = int(os.environ.get('FLASK_RUN_PORT', 5010))
    app.run(port=port)
