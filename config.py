import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration settings for the application"""
    # Secret key for form CSRF protection and session security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail server settings (for password reset, etc.)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    ADMINS = ['admin@example.com']

    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limit
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif', '.jpeg', '.pdf', '.doc', '.docx']

    # Security settings
    REMEMBER_COOKIE_DURATION = 2592000  # 30 days in seconds
    REMEMBER_COOKIE_SECURE = False  # Set to True in production
    REMEMBER_COOKIE_HTTPONLY = True

    # Caching settings
    CACHE_TYPE = 'SimpleCache'  # Use 'RedisCache' in production
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    CACHE_THRESHOLD = 500  # Maximum number of items the cache will store

    # Performance settings
    SQLALCHEMY_RECORD_QUERIES = True  # Set to False in production
    SLOW_DB_QUERY_TIME = 0.5  # Time in seconds after which a query is considered slow

    # Server settings
    SERVER_NAME = os.environ.get('SERVER_NAME')
    PREFERRED_URL_SCHEME = 'http'

    @classmethod
    def init_app(cls, app):
        """Initialize application with this configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration settings"""
    DEBUG = True
    TESTING = False

    # Development-specific settings
    SQLALCHEMY_ECHO = True  # Log SQL queries

    # Development server
    SERVER_NAME = 'localhost:5010'

class TestingConfig(Config):
    """Testing configuration settings"""
    DEBUG = False
    TESTING = True

    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

    # Disable CSRF protection in tests
    WTF_CSRF_ENABLED = False

    # Testing server
    SERVER_NAME = 'localhost:5010'

class ProductionConfig(Config):
    """Production configuration settings"""
    DEBUG = False
    TESTING = False

    # Security settings
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

    # Use Redis for caching in production
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')

    # Performance settings
    SQLALCHEMY_RECORD_QUERIES = False

    # Use HTTPS in production
    PREFERRED_URL_SCHEME = 'https'

    # Content Security Policy
    CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com",
        'style-src': "'self' 'unsafe-inline' cdn.jsdelivr.net fonts.googleapis.com cdnjs.cloudflare.com",
        'font-src': "'self' fonts.gstatic.com cdnjs.cloudflare.com",
        'img-src': "'self' data:",
        'connect-src': "'self'"
    }

    @classmethod
    def init_app(cls, app):
        """Initialize production application"""
        Config.init_app(app)

        # Email errors to administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None

        if app.config.get('MAIL_USERNAME'):
            credentials = (app.config.get('MAIL_USERNAME'), app.config.get('MAIL_PASSWORD'))
            if app.config.get('MAIL_USE_TLS'):
                secure = ()

        mail_handler = SMTPHandler(
            mailhost=(app.config.get('MAIL_SERVER'), app.config.get('MAIL_PORT')),
            fromaddr=app.config.get('MAIL_DEFAULT_SENDER'),
            toaddrs=app.config.get('ADMINS'),
            subject='Application Error',
            credentials=credentials,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
