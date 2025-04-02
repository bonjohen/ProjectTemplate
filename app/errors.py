from flask import render_template, request, jsonify
import logging
from logging.handlers import RotatingFileHandler
import os

def register_error_handlers(app):
    """Register error handlers for the application"""

    # Set up logging
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')

        # Set up file handler for logging
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)

        # Add handlers to app logger
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')

    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 errors"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Bad request', 'message': str(error)}), 400
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Forbidden', 'message': 'You do not have permission to access this resource'}), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found', 'message': 'The requested resource was not found'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        """Handle 405 errors"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Method not allowed', 'message': 'The method is not allowed for the requested URL'}), 405
        return render_template('errors/405.html'), 405

    @app.errorhandler(429)
    def too_many_requests_error(error):
        """Handle 429 errors"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Too many requests', 'message': 'Rate limit exceeded'}), 429
        return render_template('errors/429.html'), 429

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        app.logger.error('Server Error: %s', str(error))
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        """Handle unhandled exceptions"""
        app.logger.error('Unhandled Exception: %s', str(error), exc_info=True)
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500
        return render_template('errors/500.html'), 500
