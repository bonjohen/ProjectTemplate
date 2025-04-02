from app import create_app, db
from app.models import User

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Add database and models to flask shell context"""
    return {'db': db, 'User': User}

if __name__ == '__main__':
    app.run(debug=True)
