"""
@file wsgi.py
@brief WSGI entry point for the Flask application.

@details This module sets up the WSGI application to be served by a WSGI server
            like Gunicorn or uWSGI. It allows running the app in production.

@author Pressname, Inflac
@date 2024-12-26
"""

from app import app

if __name__ == "__main__":
    app.run()