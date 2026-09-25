"""
AI Workshop Management System - Main Entry Point
AI-Augmented SDLC Project
"""

import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from flask import Flask, redirect, url_for, session, request, abort
from hmac import compare_digest
from database.db import init_db
from routes.auth_routes import auth_bp
from routes.workshop_routes import workshop_bp
from routes.api_routes import api_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY') or secrets.token_hex(32)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    @app.context_processor
    def csrf_context():
        def csrf_token():
            if '_csrf_token' not in session:
                session['_csrf_token'] = secrets.token_urlsafe(32)
            return session['_csrf_token']
        return {'csrf_token': csrf_token}

    @app.before_request
    def verify_csrf():
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE') and not app.config.get('TESTING'):
            expected = session.get('_csrf_token', '')
            provided = request.form.get('csrf_token', '') or request.headers.get('X-CSRF-Token', '')
            if not expected or not compare_digest(expected, provided):
                abort(400, description='Biểu mẫu đã hết hạn hoặc thiếu mã bảo vệ. Tải lại trang và thử lại.')

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(workshop_bp)
    app.register_blueprint(api_bp)

    # Initialize database on startup
    with app.app_context():
        init_db()

    # Register AI Blueprint if available
    try:
        from routes.ai_routes import ai_bp
        app.register_blueprint(ai_bp)
    except ImportError:
        pass

    @app.route('/')
    def root():
        if session.get('user_role') == 'Admin':
            return redirect(url_for('auth.manage_users'))
        return redirect(url_for('workshop.dashboard'))

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_DEBUG', '1').lower() in ('1', 'true', 'yes')
    host = os.getenv('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=debug_mode)


